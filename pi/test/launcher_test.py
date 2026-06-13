#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Integration test for launcher.py shutdown handling.

Scenario:
- start launcher with a temporary minimal config
- publish cmd.shutdown on the bus
- expect launcher process to exit cleanly
"""

from __future__ import annotations

import argparse
import configparser
import os
import subprocess
import sys
import tempfile
import textwrap
import time

import oroverlib as orover

from bus_testlib import BusProbe, build_message, default_config_path, enum_to_topic, read_eventbus_config


def _make_temp_launcher_config(base_config_path: str, workspace_dir: str) -> str:
    cfg = configparser.ConfigParser()
    if not cfg.read(base_config_path):
        raise FileNotFoundError(f"Could not read config file: {base_config_path}")

    # Ensure scripts section exists and has at least one lightweight child.
    if not cfg.has_section("scripts"):
        cfg.add_section("scripts")

    dummy_script = os.path.join(workspace_dir, "dummy_child.py")
    with open(dummy_script, "w", encoding="utf-8") as f:
        f.write(
            textwrap.dedent(
                """
                #!/usr/bin/env python3
                import time
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                """
            ).lstrip()
        )

    if not cfg.has_section("scripts"):
        cfg.add_section("scripts")
    cfg.set("scripts", "dummy", dummy_script)

    out_path = os.path.join(workspace_dir, "launcher_test_config.ini")
    with open(out_path, "w", encoding="utf-8") as f:
        cfg.write(f)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Test launcher cmd.shutdown handling")
    parser.add_argument("--config", default=default_config_path(), help="Base config.ini path")
    parser.add_argument("--timeout", type=float, default=8.0, help="Seconds to wait for launcher shutdown")
    args = parser.parse_args()

    pub_endpoint, sub_endpoint = read_eventbus_config(args.config)
    launcher_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "launcher.py"))

    with tempfile.TemporaryDirectory(prefix="orover_launcher_test_") as tmpdir:
        test_cfg = _make_temp_launcher_config(args.config, tmpdir)

        proc = subprocess.Popen(
            [sys.executable, launcher_path, f"--config={test_cfg}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Let launcher initialize and subscribe on the bus.
        time.sleep(1.2)

        if proc.poll() is not None:
            print(f"FAIL: launcher exited early with code {proc.returncode}")
            return 1

        shutdown_msg = build_message(
            src=orover.origin.orover_stopper,
            reason=orover.cmd.shutdown,
            body={"value": "launcher_test"},
            me="launcher_test",
        )

        with BusProbe(pub_endpoint, sub_endpoint, subscriptions=[enum_to_topic(orover.cmd.shutdown)]) as probe:
            probe.publish(enum_to_topic(orover.cmd.shutdown), shutdown_msg, repeat=3)

        deadline = time.time() + args.timeout
        while time.time() < deadline:
            if proc.poll() is not None:
                print("PASS: launcher exited after cmd.shutdown")
                return 0
            time.sleep(0.1)

        proc.terminate()
        try:
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()

        print("FAIL: launcher did not exit after cmd.shutdown")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
