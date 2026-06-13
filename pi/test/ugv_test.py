#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Integration tests for ugv.py bus behavior.

Default scenario:
- publish cmd.set_motor_speed
- expect configured feedback topic from ugv telemetry path

This test is reusable by changing --expect-topic and source filters.
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


def _parse_sources(text: str) -> set[int]:
    if not text.strip():
        return set()
    out: set[int] = set()
    for name in [x.strip() for x in text.split(",") if x.strip()]:
        # Supports names from origin enum, e.g. sensor_imu, orover_ugv.
        out.add(int(orover.origin[name]))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Test ugv.py command/feedback over event bus")
    parser.add_argument("--config", default=default_config_path(), help="Path to config.ini")
    parser.add_argument("--left-speed", type=float, default=0.25, help="Left speed command value")
    parser.add_argument("--right-speed", type=float, default=0.25, help="Right speed command value")
    parser.add_argument(
        "--expect-topic",
        default=enum_to_topic(orover.state.actuator_speed),
        help="Expected follow-up topic (e.g. state.actuator_speed, state.motion, state.sensor_status)",
    )
    parser.add_argument(
        "--expect-sources",
        default="orover_ugv,sensor_imu,sensor_battery",
        help="Comma-separated origin enum names that are acceptable sources",
    )
    parser.add_argument("--timeout", type=float, default=8.0, help="Expectation timeout in seconds")
    args = parser.parse_args()

    allowed_sources = _parse_sources(args.expect_sources)
    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)

    command = build_message(
        src=orover.controller.remote_interface,
        reason=orover.cmd.set_motor_speed,
        body={"left_speed": args.left_speed, "right_speed": args.right_speed},
        me="ugv_test",
    )

    expected = Expectation(
        description=(
            f"ugv should emit {args.expect_topic} after cmd.set_motor_speed "
            f"from one of sources={sorted(allowed_sources)}"
        ),
        topic=args.expect_topic,
        timeout=args.timeout,
        validator=lambda msg: (
            not allowed_sources or int(msg.get("src", -1)) in allowed_sources
        ),
    )

    print(f"INFO: config={args.config}")
    print(f"INFO: pub={pub_endpoint} sub={sub_endpoint}")
    print("INFO: scenario=set_motor_speed_feedback")
    print(f"INFO: expect_topic={args.expect_topic} expect_sources={args.expect_sources}")

    subs = [args.expect_topic]
    with BusProbe(pub_endpoint, sub_endpoint, subscriptions=subs) as probe:
        ok, details = run_scenario(
            probe=probe,
            publish_topic=enum_to_topic(orover.cmd.set_motor_speed),
            publish_message=command,
            expectations=[expected],
        )

    for line in details:
        print(line)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
