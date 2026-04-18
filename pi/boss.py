#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  The BOSS server for the ROVER. Handles messages related to
                  object recognition, versatile exploration, and navigation state.
"""

import math
import time
import threading
import oroverlib as orover
from base_process import baseprocess


# ---------------------------------------------------------------------------
# Navigation helper functions 
# ---------------------------------------------------------------------------

def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _update_pose_from_motion(heading, left_speed, right_speed):
    now = time.time()
    dt = max(0.0, now - p.nav_state["kinematics"]["last_time"])
    p.nav_state["kinematics"]["last_time"] = now

    if heading is not None:
        p.nav_state["pose"]["heading_deg"] = heading

    if left_speed is None or right_speed is None:
        return

    v = 0.5 * (left_speed + right_speed)
    theta = math.radians(p.nav_state["pose"].get("heading_deg", 0.0) or 0.0)
    p.nav_state["pose"]["x_m"] += v * dt * math.cos(theta)
    p.nav_state["pose"]["y_m"] += v * dt * math.sin(theta)


def _sensor_to_angle_rad(sensor_name):
    if "left" in sensor_name:
        return math.pi / 2.0
    if "right" in sensor_name:
        return -math.pi / 2.0
    if "rear" in sensor_name:
        return math.pi
    return 0.0


def _world_to_grid(x_m, y_m):
    origin = p.nav_state["grid"]["origin_cell"]
    res = p.nav_state["grid"]["resolution_m"]
    gx = int(round(origin + (x_m / res)))
    gy = int(round(origin + (y_m / res)))
    return gx, gy


def _mark_cell(gx, gy, value):
    size = p.nav_state["grid"]["size"]
    if 0 <= gx < size and 0 <= gy < size:
        p.nav_state["grid"]["cells"][gy][gx] = value


def _update_grid_with_obstacle(src, distance_cm):
    d_cm = _as_float(distance_cm)
    if d_cm is None or d_cm <= 0:
        return

    d_m = d_cm / 100.0
    max_range = p.nav_state["grid"]["max_obstacle_range_m"]
    if d_m > max_range:
        return

    sensor_name = p.enum_to_name(src) or ""
    heading_deg = p.nav_state["pose"].get("heading_deg", 0.0) or 0.0
    theta = math.radians(heading_deg) + _sensor_to_angle_rad(sensor_name.lower())

    x0 = p.nav_state["pose"]["x_m"]
    y0 = p.nav_state["pose"]["y_m"]
    x1 = x0 + d_m * math.cos(theta)
    y1 = y0 + d_m * math.sin(theta)

    gx0, gy0 = _world_to_grid(x0, y0)
    gx1, gy1 = _world_to_grid(x1, y1)

    _mark_cell(gx0, gy0, 0.25)
    _mark_cell(gx1, gy1, 1.0)


def _grid_preview(cells, max_size=21):
    size = len(cells)
    if size <= max_size:
        return cells
    start = (size - max_size) // 2
    end = start + max_size
    return [row[start:end] for row in cells[start:end]]


def _build_snapshot_payload():
    pose = p.nav_state["pose"]
    grid = p.nav_state["grid"]
    motion = p.nav_state.get("motion", {})
    obstacles = p.nav_state.get("obstacles", {})

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
        "battery_voltage": p.nav_state.get("battery_voltage"),
        "obstacle_count": len(obstacles),
        "grid": {
            "resolution_m": grid["resolution_m"],
            "preview": _grid_preview(grid["cells"], max_size=grid["preview_size"]),
        },
        "ts": p.nav_state.get("last_update_ts"),
    }


def publish_pose_loop(interval_s):
    while p.running:
        time.sleep(interval_s)
        p.nav_state_lock.acquire()
        try:
            payload = _build_snapshot_payload()
        finally:
            p.nav_state_lock.release()

        p.send_event(
            src=orover.origin.orover_boss,
            reason=orover.state.pose,
            body=payload,
        )


def snapshot_logger_loop(log_interval_s):
    """Low-rate debug logger to verify navigation pipeline is alive."""
    while p.running:
        time.sleep(log_interval_s)
        p.nav_state_lock.acquire()
        try:
            motion = p.nav_state.get("motion", {})
            obstacles = p.nav_state.get("obstacles", {})
            pose = p.nav_state.get("pose", {})
            p.logger.debug(
                "navigation snapshot: x=%.2f y=%.2f heading=%s L=%s R=%s batt=%sV obstacles=%d",
                float(pose.get("x_m", 0.0) or 0.0),
                float(pose.get("y_m", 0.0) or 0.0),
                motion.get("heading"),
                motion.get("left_speed"),
                motion.get("right_speed"),
                p.nav_state.get("battery_voltage"),
                len(obstacles),
            )
        finally:
            p.nav_state_lock.release()


# ---------------------------------------------------------------------------
# Message handlers
# ---------------------------------------------------------------------------

class handler:
    """ Contains the handlers for BOSS messages. Each handler takes a message as input and returns a result string.
        The handlers are called by the BOSS server when a message with the corresponding reason is received.
        Handlers do not return a response to the sender, but can perform actions based on the message content,
        like logging or sending new messages to the bus.

        Each message is expected to have the following structure:

            "id"    : UUID
           ,"ts"    : datetime of message in '%Y-%m-%dT%H:%M:%S.%f' format
           ,"src"   : message source, e.g. specific sensor or actuator, should be in class origin
           ,"me"    : sending script name
           ,"host"  : sending node
           ,"prio"  : priority of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"reason": type of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"body"  : JSON; contains parameters depending on type of message
    """

    def event_heartbeat(self, msg):
        global heartbeats
        if "me" in msg and "ts" in msg:
           heartbeats[msg["me"]] = msg["ts"]
           p.logger.debug(f"Stored heartbeat from {msg['me']}")
        return True


    def event_object_detected(self, message):
        sensor = p.enum_to_name(message.get('src'))
        body = message.get('body', {})
        if "distance" not in body:
            p.logger.warning(f"Discarded for sensor {sensor}: missing distance parameter in body")
            return False

        d = body.get('distance', 0)
        if d < 0:
            p.logger.warning(f"Discarded for sensor {sensor}: distance {d} is negative")
            return False

        p.nav_state_lock.acquire()
        try:
            p.nav_state["obstacles"][str(sensor)] = {
                "distance": d,
                "ts": message.get("ts"),
            }
            _update_grid_with_obstacle(message.get('src'), d)
            p.nav_state["last_update_ts"] = message.get("ts")
        finally:
            p.nav_state_lock.release()

        #print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
        return True


    def state_motion(self, message):
        body = message.get("body", {})
        p.nav_state_lock.acquire()
        try:
            heading = _as_float(body.get("heading"))
            left_speed = _as_float(body.get("left_speed"))
            right_speed = _as_float(body.get("right_speed"))

            p.nav_state["motion"] = {
                "heading": heading,
                "pitch": body.get("pitch"),
                "roll": body.get("roll"),
                "left_speed": left_speed,
                "right_speed": right_speed,
                "ts": message.get("ts"),
            }

            _update_pose_from_motion(heading, left_speed, right_speed)
            p.nav_state["last_update_ts"] = message.get("ts")
        finally:
            p.nav_state_lock.release()
        return True


    def state_battery(self, message):
        body = message.get("body", {})
        p.nav_state_lock.acquire()
        try:
            p.nav_state["battery_voltage"] = body.get("voltage")
            p.nav_state["last_update_ts"] = message.get("ts")
        finally:
            p.nav_state_lock.release()
        return True


class base(baseprocess):
    pass


#### Main execution starts here ####
if __name__ == "__main__":

    heartbeats = {}

    h = handler()
    p = base(handler=h)

    # Initialise navigation state (merged from navigation.py)
    p.nav_state_lock = threading.Lock()
    p.nav_state = {
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
            "size": p.config.getint("boss", "grid_size", fallback=81),
            "resolution_m": p.config.getfloat("boss", "grid_resolution_m", fallback=0.10),
            "max_obstacle_range_m": p.config.getfloat("boss", "max_obstacle_range_m", fallback=3.5),
            "preview_size": p.config.getint("boss", "grid_preview_size", fallback=21),
            "origin_cell": 0,
            "cells": [],
        },
        "last_update_ts": None,
    }
    p.nav_state["grid"]["origin_cell"] = p.nav_state["grid"]["size"] // 2
    p.nav_state["grid"]["cells"] = [
        [0.0 for _ in range(p.nav_state["grid"]["size"])]
        for _ in range(p.nav_state["grid"]["size"])
    ]

    log_interval = p.config.getfloat("boss", "snapshot_log_interval", fallback=5.0)
    if log_interval > 0:
        threading.Thread(target=snapshot_logger_loop, args=(log_interval,), daemon=True).start()

    publish_interval = p.config.getfloat("boss", "pose_publish_interval", fallback=0.5)
    if publish_interval > 0:
        threading.Thread(target=publish_pose_loop, args=(publish_interval,), daemon=True).start()

    p.run()