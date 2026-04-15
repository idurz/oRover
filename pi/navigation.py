#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Observe-only navigation process scaffold.
"""

#     This process is intentionally passive in the first integration step:
#     - subscribes to motion, battery and obstacle events
#     - keeps an internal navigation snapshot for future SLAM/planner integration
#     - does not publish motor commands


import math
import time
import threading
import oroverlib as orover
from base_process import baseprocess

class handler:
    """Message handlers for passive navigation state collection."""

    def state_motion(self, message):
        body = message.get("body", {})
        n.nav_state_lock.acquire()
        try:
            heading = _as_float(body.get("heading"))
            left_speed = _as_float(body.get("left_speed"))
            right_speed = _as_float(body.get("right_speed"))

            n.nav_state["motion"] = {
                "heading": heading,
                "pitch": body.get("pitch"),
                "roll": body.get("roll"),
                "left_speed": left_speed,
                "right_speed": right_speed,
                "ts": message.get("ts"),
            }

            _update_pose_from_motion(heading, left_speed, right_speed)
            n.nav_state["last_update_ts"] = message.get("ts")
        finally:
            n.nav_state_lock.release()
        return True

    def state_battery(self, message):
        body = message.get("body", {})
        n.nav_state_lock.acquire()
        try:
            n.nav_state["battery_voltage"] = body.get("voltage")
            n.nav_state["last_update_ts"] = message.get("ts")
        finally:
            n.nav_state_lock.release()
        return True

    def event_object_detected(self, message):
        body = message.get("body", {})
        src = message.get("src")

        n.nav_state_lock.acquire()
        try:
            n.nav_state["obstacles"][str(src)] = {
                "distance": body.get("distance"),
                "ts": message.get("ts"),
            }
            _update_grid_with_obstacle(src, body.get("distance"))
            n.nav_state["last_update_ts"] = message.get("ts")
        finally:
            n.nav_state_lock.release()
        return True


class base(baseprocess):
    pass


def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _update_pose_from_motion(heading, left_speed, right_speed):
    now = time.time()
    dt = max(0.0, now - n.nav_state["kinematics"]["last_time"])
    n.nav_state["kinematics"]["last_time"] = now

    # Heading is provided in degrees in upstream message.
    if heading is not None:
        n.nav_state["pose"]["heading_deg"] = heading

    if left_speed is None or right_speed is None:
        return

    v = 0.5 * (left_speed + right_speed)
    theta = math.radians(n.nav_state["pose"].get("heading_deg", 0.0) or 0.0)
    n.nav_state["pose"]["x_m"] += v * dt * math.cos(theta)
    n.nav_state["pose"]["y_m"] += v * dt * math.sin(theta)


def _sensor_to_angle_rad(sensor_name):
    # Very simple fixed mounting assumptions for first safe integration.
    if "left" in sensor_name:
        return math.pi / 2.0
    if "right" in sensor_name:
        return -math.pi / 2.0
    if "rear" in sensor_name:
        return math.pi
    return 0.0


def _world_to_grid(x_m, y_m):
    origin = n.nav_state["grid"]["origin_cell"]
    res = n.nav_state["grid"]["resolution_m"]
    gx = int(round(origin + (x_m / res)))
    gy = int(round(origin + (y_m / res)))
    return gx, gy


def _mark_cell(gx, gy, value):
    size = n.nav_state["grid"]["size"]
    if 0 <= gx < size and 0 <= gy < size:
        n.nav_state["grid"]["cells"][gy][gx] = value


def _update_grid_with_obstacle(src, distance_cm):
    d_cm = _as_float(distance_cm)
    if d_cm is None or d_cm <= 0:
        return

    d_m = d_cm / 100.0
    max_range = n.nav_state["grid"]["max_obstacle_range_m"]
    if d_m > max_range:
        return

    sensor_name = n.enum_to_name(src) or ""
    heading_deg = n.nav_state["pose"].get("heading_deg", 0.0) or 0.0
    theta = math.radians(heading_deg) + _sensor_to_angle_rad(sensor_name.lower())

    x0 = n.nav_state["pose"]["x_m"]
    y0 = n.nav_state["pose"]["y_m"]
    x1 = x0 + d_m * math.cos(theta)
    y1 = y0 + d_m * math.sin(theta)

    gx0, gy0 = _world_to_grid(x0, y0)
    gx1, gy1 = _world_to_grid(x1, y1)

    _mark_cell(gx0, gy0, 0.25)
    _mark_cell(gx1, gy1, 1.0)


def _grid_preview(cells, max_size=21):
    # Return a compact center crop to keep bus payload small.
    size = len(cells)
    if size <= max_size:
        return cells
    start = (size - max_size) // 2
    end = start + max_size
    return [row[start:end] for row in cells[start:end]]


def _build_snapshot_payload():
    pose = n.nav_state["pose"]
    grid = n.nav_state["grid"]
    motion = n.nav_state.get("motion", {})
    obstacles = n.nav_state.get("obstacles", {})

    return {
        "pose": {
            "x_m": round(pose["x_m"], 3),
            "y_m": round(pose["y_m"], 3),
            "heading_deg": round(float(pose.get("heading_deg", 0.0) or 0.0), 2),
        },
        "speed": {
            "left_mps": motion.get("left_speed"),
            "right_mps": motion.get("right_speed"),
        },
        "battery_voltage": n.nav_state.get("battery_voltage"),
        "obstacle_count": len(obstacles),
        "grid": {
            "resolution_m": grid["resolution_m"],
            "preview": _grid_preview(grid["cells"], max_size=grid["preview_size"]),
        },
        "ts": n.nav_state.get("last_update_ts"),
    }


def publish_pose_loop(interval_s):
    while n.running:
        time.sleep(interval_s)
        n.nav_state_lock.acquire()
        try:
            payload = _build_snapshot_payload()
        finally:
            n.nav_state_lock.release()

        n.send_event(
            src=orover.origin.orover_navi,
            reason=orover.state.pose,
            body=payload,
        )


def snapshot_logger_loop(log_interval_s):
    """Low-rate debug logger to verify observe-only pipeline is alive."""
    while n.running:
        time.sleep(log_interval_s)
        n.nav_state_lock.acquire()
        try:
            motion = n.nav_state.get("motion", {})
            obstacles = n.nav_state.get("obstacles", {})
            pose = n.nav_state.get("pose", {})
            n.logger.debug(
                "navigation snapshot: x=%.2f y=%.2f heading=%s L=%s R=%s batt=%sV obstacles=%d",
                float(pose.get("x_m", 0.0) or 0.0),
                float(pose.get("y_m", 0.0) or 0.0),
                motion.get("heading"),
                motion.get("left_speed"),
                motion.get("right_speed"),
                n.nav_state.get("battery_voltage"),
                len(obstacles),
            )
        finally:
            n.nav_state_lock.release()


if __name__ == "__main__":
    h = handler()
    n = base(handler=h)

    n.nav_state_lock = threading.Lock()
    n.nav_state = {
        "motion": {},
        "obstacles": {},
        "battery_voltage": None,
        "pose": {
            "x_m": 0.0,
            "y_m": 0.0,
            "heading_deg": 0.0,
        },
        "kinematics": {
            "last_time": time.time(),
        },
        "grid": {
            "size": n.config.getint("navigation", "grid_size", fallback=81),
            "resolution_m": n.config.getfloat("navigation", "grid_resolution_m", fallback=0.10),
            "max_obstacle_range_m": n.config.getfloat("navigation", "max_obstacle_range_m", fallback=3.5),
            "preview_size": n.config.getint("navigation", "grid_preview_size", fallback=21),
            "origin_cell": 0,
            "cells": [],
        },
        "last_update_ts": None,
    }
    n.nav_state["grid"]["origin_cell"] = n.nav_state["grid"]["size"] // 2
    n.nav_state["grid"]["cells"] = [
        [0.0 for _ in range(n.nav_state["grid"]["size"])]
        for _ in range(n.nav_state["grid"]["size"])
    ]

    log_interval = n.config.getfloat("navigation", "snapshot_log_interval", fallback=5.0)
    if log_interval > 0:
        threading.Thread(target=snapshot_logger_loop, args=(log_interval,), daemon=True).start()

    publish_interval = n.config.getfloat("navigation", "pose_publish_interval", fallback=0.5)
    if publish_interval > 0:
        threading.Thread(target=publish_pose_loop, args=(publish_interval,), daemon=True).start()

    n.logger.info("navigation process started in observe-only mode")
    n.run()
