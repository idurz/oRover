#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Publish synthetic state.pose messages that trace a 1 x 2 meter rectangle.

This script is intended to drive the grid preview in grid.html without real hardware.
By default it loops forever until Ctrl+C.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_PI_DIR = os.path.abspath(os.path.join(_HERE, ".."))
if _PI_DIR not in sys.path:
    sys.path.insert(0, _PI_DIR)

import oroverlib as orover

from bus_testlib import BusProbe, build_message, default_config_path, enum_to_topic, read_eventbus_config


def _linspace(start: float, stop: float, steps: int) -> list[float]:
    if steps <= 1:
        return [start]
    delta = (stop - start) / float(steps - 1)
    return [start + i * delta for i in range(steps)]


def _world_to_cell(x_m: float, y_m: float, cells: int, span_x_m: float, span_y_m: float) -> tuple[int, int]:
    # Map world coordinates in [-span/2, span/2] onto grid indices.
    nx = 0.0 if span_x_m <= 0 else (x_m + span_x_m / 2.0) / span_x_m
    ny = 0.0 if span_y_m <= 0 else (y_m + span_y_m / 2.0) / span_y_m
    nx = min(1.0, max(0.0, nx))
    ny = min(1.0, max(0.0, ny))

    col = int(round(nx * (cells - 1)))
    row = int(round((1.0 - ny) * (cells - 1)))
    return row, col


def _build_rect_trajectory(
    width_m: float,
    height_m: float,
    step_m: float,
    start_from_center: bool = False,
) -> list[tuple[float, float, float]]:
    # Rectangle corners centered at origin.
    x0, x1 = -width_m / 2.0, width_m / 2.0
    y0, y1 = -height_m / 2.0, height_m / 2.0

    n_w = max(2, int(round(width_m / step_m)) + 1)
    n_h = max(2, int(round(height_m / step_m)) + 1)

    points: list[tuple[float, float, float]] = []

    # Bottom edge: left -> right (heading 0 deg)
    for x in _linspace(x0, x1, n_w):
        points.append((x, y0, 0.0))

    # Right edge: bottom -> top (heading 90 deg)
    for y in _linspace(y0, y1, n_h)[1:]:
        points.append((x1, y, 90.0))

    # Top edge: right -> left (heading 180 deg)
    for x in _linspace(x1, x0, n_w)[1:]:
        points.append((x, y1, 180.0))

    # Left edge: top -> bottom (heading 270 deg)
    for y in _linspace(y1, y0, n_h)[1:]:
        points.append((x0, y, 270.0))

    if start_from_center:
        center_x, center_y = 0.0, 0.0
        dx = x0 - center_x
        dy = y0 - center_y
        dist = math.hypot(dx, dy)
        heading_to_corner = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
        n_center = max(2, int(round(dist / step_m)) + 1)
        approach = [
            (x, y, heading_to_corner)
            for x, y in zip(_linspace(center_x, x0, n_center), _linspace(center_y, y0, n_center))
        ]
        return approach + points[1:]

    return points


def _empty_grid(cells: int) -> list[list[float]]:
    return [[0.0 for _ in range(cells)] for _ in range(cells)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish synthetic rectangular pose data for grid.html")
    parser.add_argument("--config", default=default_config_path(), help="Path to config/config.ini")
    parser.add_argument("--width", type=float, default=1.0, help="Rectangle width in meters (default: 1.0)")
    parser.add_argument("--height", type=float, default=2.0, help="Rectangle height in meters (default: 2.0)")
    parser.add_argument("--step", type=float, default=0.05, help="Step size in meters along edges (default: 0.05)")
    parser.add_argument("--interval", type=float, default=0.25, help="Publish interval per pose in seconds (default: 0.25)")
    parser.add_argument("--cells", type=int, default=41, help="Preview grid size NxN (default: 41)")
    parser.add_argument("--loops", type=int, default=1, help="Number of rectangle loops (0 = infinite)")
    parser.add_argument("--start-center", action="store_true", help="Start in center (0,0), then move to rectangle and trace it")
    args = parser.parse_args()

    if args.width <= 0 or args.height <= 0 or args.step <= 0 or args.interval <= 0:
        raise SystemExit("width, height, step and interval must be > 0")

    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)
    topic = enum_to_topic(orover.state.pose)

    trajectory = _build_rect_trajectory(args.width, args.height, args.step, start_from_center=args.start_center)
    if not trajectory:
        raise SystemExit("No trajectory points generated")

    print(f"INFO: config={args.config}")
    print(f"INFO: pub={pub_endpoint} sub={sub_endpoint}")
    print(f"INFO: rectangle={args.width}m x {args.height}m, points_per_loop={len(trajectory)}")
    print("INFO: publishing state.pose as src=orover_boss for app.py compatibility")

    span_x = max(args.width * 1.4, 2.5)
    span_y = max(args.height * 1.4, 3.0)

    loops_done = 0
    probe = BusProbe(pub_endpoint, sub_endpoint, subscriptions=[])
    with probe:
        try:
            trail: set[tuple[int, int]] = set()
            while args.loops == 0 or loops_done < args.loops:
                for x_m, y_m, heading_deg in trajectory:
                    row, col = _world_to_cell(x_m, y_m, args.cells, span_x, span_y)
                    trail.add((row, col))

                    preview = _empty_grid(args.cells)
                    for r, c in trail:
                        preview[r][c] = 0.25

                    body = {
                        "pose": {
                            "x_m": round(x_m, 3),
                            "y_m": round(y_m, 3),
                            "heading_deg": round(heading_deg, 2),
                        },
                        "grid": {"preview": preview},
                        "ts": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    }

                    msg = build_message(
                        src=orover.origin.orover_boss,
                        reason=orover.state.pose,
                        body=body,
                        me="pose_rectangle_test",
                    )
                    probe.publish(topic, msg, repeat=1, interval_s=0.0)
                    time.sleep(args.interval)

                loops_done += 1

        except KeyboardInterrupt:
            print("\nINFO: stopped by user")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
