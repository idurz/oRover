#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reusable helpers for event bus integration tests.

This module provides a small PUB/SUB client and scenario runner so process
specific tests can focus on payloads and expectations.
"""

from __future__ import annotations

import configparser
import datetime as _dt
import json
import os
import socket
import sys
import time
import uuid
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable

import zmq

# Ensure imports from pi/ are available when running tests from pi/test.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PI_DIR = os.path.abspath(os.path.join(_HERE, ".."))
if _PI_DIR not in sys.path:
    sys.path.insert(0, _PI_DIR)

import oroverlib as orover


def read_eventbus_config(config_path: str) -> tuple[str, str]:
    """Read PUB/SUB client endpoints from config.ini."""
    cfg = configparser.ConfigParser()
    if not cfg.read(config_path):
        raise FileNotFoundError(f"Could not read config file: {config_path}")

    pub_endpoint = cfg.get("eventbus", "client_pub_socket", fallback="tcp://localhost:5556")
    sub_endpoint = cfg.get("eventbus", "client_sub_socket", fallback="tcp://localhost:5555")
    return pub_endpoint, sub_endpoint


def default_config_path() -> str:
    """Return default runtime config path relative to pi/test."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))


def enum_to_topic(reason: IntEnum) -> str:
    """Convert enum value to topic format used on the bus (e.g. state.battery)."""
    return f"{reason.__class__.__name__}.{reason.name}"


def build_message(
    *,
    src: IntEnum,
    reason: IntEnum,
    body: dict,
    me: str,
    prio: IntEnum = orover.priority.normal,
) -> dict:
    """Construct a bus message payload matching baseprocess.send_event format."""
    return {
        "id": str(uuid.uuid4()),
        "ts": _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "src": int(src),
        "me": me,
        "host": socket.gethostname(),
        "prio": int(prio),
        "reason": int(reason),
        "body": body,
    }


@dataclass(frozen=True)
class Expectation:
    """Single expected event assertion for a test scenario."""

    description: str
    topic: str
    validator: Callable[[dict], bool]
    timeout: float = 5.0


class BusProbe:
    """Minimal PUB/SUB helper for integration tests."""

    def __init__(self, pub_endpoint: str, sub_endpoint: str, subscriptions: list[str], join_delay_s: float = 0.4):
        self.pub_endpoint = pub_endpoint
        self.sub_endpoint = sub_endpoint
        self.subscriptions = subscriptions
        self.join_delay_s = join_delay_s

        self.ctx = zmq.Context.instance()
        self.pub = self.ctx.socket(zmq.PUB)
        self.sub = self.ctx.socket(zmq.SUB)
        self.poller = zmq.Poller()

    def __enter__(self) -> "BusProbe":
        self.sub.connect(self.sub_endpoint)
        for topic in self.subscriptions:
            self.sub.setsockopt_string(zmq.SUBSCRIBE, topic)

        self.pub.connect(self.pub_endpoint)
        self.poller.register(self.sub, zmq.POLLIN)

        # Slow-joiner mitigation for SUB subscriptions.
        time.sleep(self.join_delay_s)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.sub.close(0)
        self.pub.close(0)

    def publish(self, topic: str, message: dict, repeat: int = 2, interval_s: float = 0.05) -> None:
        wire = f"{topic} {json.dumps(message)}"
        for _ in range(max(1, repeat)):
            self.pub.send_string(wire)
            time.sleep(interval_s)

    def wait_for(self, expectation: Expectation) -> tuple[bool, str]:
        deadline = time.time() + expectation.timeout
        while time.time() < deadline:
            socks = dict(self.poller.poll(150))
            if self.sub not in socks or socks[self.sub] != zmq.POLLIN:
                continue

            raw = self.sub.recv_string()
            if " " not in raw:
                continue

            topic, payload = raw.split(" ", 1)
            if topic != expectation.topic:
                continue

            try:
                msg = json.loads(payload)
            except json.JSONDecodeError:
                continue

            if expectation.validator(msg):
                return True, f"Matched {expectation.topic}: {expectation.description}"

        return False, f"Timed out waiting for {expectation.topic}: {expectation.description}"


def run_scenario(
    *,
    probe: BusProbe,
    publish_topic: str,
    publish_message: dict,
    expectations: list[Expectation],
    publish_repeat: int = 3,
) -> tuple[bool, list[str]]:
    """Publish one command/event and validate expected follow-up event(s)."""
    probe.publish(publish_topic, publish_message, repeat=publish_repeat)

    results: list[str] = []
    ok = True
    for exp in expectations:
        passed, details = probe.wait_for(exp)
        results.append(("PASS: " if passed else "FAIL: ") + details)
        ok = ok and passed

    return ok, results
