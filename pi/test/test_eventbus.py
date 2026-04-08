#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple integration test program for eventbus.py.

This script verifies that a message published to the event bus publisher
endpoint is received by a subscriber on the subscriber endpoint.
"""

from __future__ import annotations

import argparse
import configparser
import os
import subprocess
import sys
import time

try:
    import zmq
except ModuleNotFoundError as exc:
    print("FAIL: missing dependency 'pyzmq'. Install with: pip install pyzmq")
    raise SystemExit(1) from exc


def read_eventbus_config(config_path: str) -> tuple[str, str]:
    """Read client bus endpoints from config.ini."""
    cfg = configparser.ConfigParser()
    if not cfg.read(config_path):
        raise FileNotFoundError(f"Could not read config file: {config_path}")

    pub_endpoint = cfg.get("eventbus", "client_pub_socket", fallback="tcp://localhost:5556")
    sub_endpoint = cfg.get("eventbus", "client_sub_socket", fallback="tcp://localhost:5555")
    return pub_endpoint, sub_endpoint


def run_test(timeout: float, topic: str, payload: str, pub_endpoint: str, sub_endpoint: str) -> None:
    """Run a PUB/SUB round-trip test through the event bus."""
    ctx = zmq.Context.instance()
    sub = ctx.socket(zmq.SUB)
    pub = ctx.socket(zmq.PUB)

    try:
        sub.connect(sub_endpoint)
        sub.setsockopt_string(zmq.SUBSCRIBE, topic)

        pub.connect(pub_endpoint)

        poller = zmq.Poller()
        poller.register(sub, zmq.POLLIN)

        expected = f"{topic} {payload}"
        deadline = time.time() + timeout

        # Slow-joiner mitigation: publish multiple times while waiting.
        while time.time() < deadline:
            pub.send_string(expected)
            socks = dict(poller.poll(200))
            if sub in socks and socks[sub] == zmq.POLLIN:
                received = sub.recv_string()
                if received == expected:
                    print(f"PASS: received expected message -> {received}")
                    return
                print(f"INFO: received different message -> {received}")

        raise TimeoutError(
            f"No expected message received within {timeout:.1f}s. "
            f"Expected: {expected}"
        )
    finally:
        sub.close(0)
        pub.close(0)
        ctx.term()


def main() -> int:
    parser = argparse.ArgumentParser(description="Test eventbus.py")
    parser.add_argument(
        "--timeout",
        type=float,
        default=6.0,
        help="Seconds to wait for message receipt (default: 6.0)",
    )
    parser.add_argument(
        "--topic",
        default="test.eventbus",
        help="Topic prefix to publish/subscribe (default: test.eventbus)",
    )
    parser.add_argument(
        "--payload",
        default="hello",
        help="Payload text after topic (default: hello)",
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"),
        help="Path to config.ini (default: pi/config.ini)",
    )
    parser.add_argument(
        "--use-existing-bus",
        action="store_true",
        help="Do not spawn eventbus.py; use already running bus",
    )
    args = parser.parse_args()

    bus_proc: subprocess.Popen[bytes] | None = None

    try:
        pub_endpoint, sub_endpoint = read_eventbus_config(args.config)
        print(f"INFO: using config {args.config}")
        print(f"INFO: publisher endpoint {pub_endpoint}")
        print(f"INFO: subscriber endpoint {sub_endpoint}")

        if not args.use_existing_bus:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bus_path = os.path.join(script_dir, "eventbus.py")

            bus_proc = subprocess.Popen(
                [sys.executable, bus_path],
                cwd=script_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Give the bus a moment to bind sockets.
            time.sleep(1.0)

            if bus_proc.poll() is not None:
                print("INFO: spawned eventbus.py exited early; trying existing bus")
                bus_proc = None

        run_test(args.timeout, args.topic, args.payload, pub_endpoint, sub_endpoint)
        return 0

    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    finally:
        if bus_proc is not None and bus_proc.poll() is None:
            bus_proc.terminate()
            try:
                bus_proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                bus_proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())