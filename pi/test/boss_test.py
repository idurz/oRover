#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Integration tests for boss.py bus behavior.

Current scenario:
- publish state.battery (low but non-critical)
- expect event.lowBattery from boss
"""

from __future__ import annotations

import argparse

import oroverlib as orover

from bus_testlib import (
    BusProbe,
    Expectation,
    build_message,
    default_config_path,
    enum_to_topic,
    read_eventbus_config,
    run_scenario,
)


def _float_matches(actual, expected: float, tol: float = 0.02) -> bool:
    try:
        return abs(float(actual) - float(expected)) <= tol
    except (TypeError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Test boss.py event handling")
    parser.add_argument("--config", default=default_config_path(), help="Path to config.ini")
    parser.add_argument(
        "--low-voltage",
        type=float,
        default=11.85,
        help="Voltage used to trigger event.lowBattery (must be above shutdown threshold)",
    )
    parser.add_argument("--timeout", type=float, default=6.0, help="Expectation timeout in seconds")
    args = parser.parse_args()

    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)

    incoming = build_message(
        src=orover.origin.sensor_battery,
        reason=orover.state.battery,
        body={"voltage": args.low_voltage},
        me="boss_test",
    )

    expected = Expectation(
        description=f"boss should publish event.lowBattery for voltage={args.low_voltage}",
        topic=enum_to_topic(orover.event.lowBattery),
        timeout=args.timeout,
        validator=lambda msg: (
            int(msg.get("src", -1)) == int(orover.origin.orover_boss)
            and int(msg.get("reason", -1)) == int(orover.event.lowBattery)
            and _float_matches((msg.get("body") or {}).get("voltage"), args.low_voltage)
        ),
    )

    print(f"INFO: config={args.config}")
    print(f"INFO: pub={pub_endpoint} sub={sub_endpoint}")
    print("INFO: scenario=low_battery_warning")

    subs = [enum_to_topic(orover.event.lowBattery)]
    with BusProbe(pub_endpoint, sub_endpoint, subscriptions=subs) as probe:
        ok, details = run_scenario(
            probe=probe,
            publish_topic=enum_to_topic(orover.state.battery),
            publish_message=incoming,
            expectations=[expected],
        )

    for line in details:
        print(line)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
