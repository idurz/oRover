#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Integration test for app.py bridge behavior.

Scenario:
- call HTTP POST /control with action
- expect cmd.set_motor_speed on bus
"""

from __future__ import annotations

import argparse
import json
import urllib.request

import oroverlib as orover

from bus_testlib import BusProbe, Expectation, default_config_path, enum_to_topic, read_eventbus_config


def _post_json(url: str, payload: dict, timeout: float) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Test app.py HTTP->bus bridge")
    parser.add_argument("--config", default=default_config_path(), help="Path to config.ini")
    parser.add_argument("--url", default="http://localhost:5000/control", help="app /control URL")
    parser.add_argument("--action", default="stop", help="Control action (forward/back/left/right/stop)")
    parser.add_argument("--timeout", type=float, default=6.0, help="Expectation timeout in seconds")
    args = parser.parse_args()

    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)
    topic = enum_to_topic(orover.cmd.set_motor_speed)

    expected = Expectation(
        description=f"app should publish cmd.set_motor_speed for action={args.action}",
        topic=topic,
        timeout=args.timeout,
        validator=lambda msg: int(msg.get("reason", -1)) == int(orover.cmd.set_motor_speed),
    )

    print(f"INFO: config={args.config}")
    print(f"INFO: pub={pub_endpoint} sub={sub_endpoint}")
    print("INFO: scenario=app_control_to_bus")

    with BusProbe(pub_endpoint, sub_endpoint, subscriptions=[topic]) as probe:
        try:
            status, body = _post_json(args.url, {"action": args.action}, timeout=args.timeout)
        except Exception as exc:
            print(f"FAIL: HTTP request to app failed: {exc}")
            return 1

        if status != 200:
            print(f"FAIL: app returned HTTP {status}: {body}")
            return 1

        passed, details = probe.wait_for(expected)
        print(("PASS: " if passed else "FAIL: ") + details)
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
