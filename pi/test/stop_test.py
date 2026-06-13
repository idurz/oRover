#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Integration test for stop.py.

Scenario:
- run stop.py as a one-shot script
- expect cmd.shutdown on bus from src=orover_stopper
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import oroverlib as orover

from bus_testlib import BusProbe, Expectation, default_config_path, enum_to_topic, read_eventbus_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Test stop.py bus publish behavior")
    parser.add_argument("--config", default=default_config_path(), help="Path to config.ini")
    parser.add_argument("--timeout", type=float, default=5.0, help="Expectation timeout in seconds")
    args = parser.parse_args()

    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)
    stop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stop.py"))

    expected = Expectation(
        description="stop.py should publish cmd.shutdown",
        topic=enum_to_topic(orover.cmd.shutdown),
        timeout=args.timeout,
        validator=lambda msg: (
            int(msg.get("src", -1)) == int(orover.origin.orover_stopper)
            and int(msg.get("reason", -1)) == int(orover.cmd.shutdown)
            and (msg.get("body") or {}).get("value") == "requested by stop.py"
        ),
    )

    print(f"INFO: config={args.config}")
    print(f"INFO: pub={pub_endpoint} sub={sub_endpoint}")
    print("INFO: scenario=stop_publishes_shutdown")

    with BusProbe(pub_endpoint, sub_endpoint, subscriptions=[enum_to_topic(orover.cmd.shutdown)]) as probe:
        proc = subprocess.run(
            [sys.executable, stop_path, f"--config={args.config}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        if proc.returncode != 0:
            print(f"FAIL: stop.py exited with code {proc.returncode}")
            return 1

        passed, details = probe.wait_for(expected)
        print(("PASS: " if passed else "FAIL: ") + details)
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
