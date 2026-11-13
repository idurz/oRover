#!/usr/bin/env python3

import json
import os
import sys
import types
import unittest
from unittest.mock import patch


PI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PI_DIR not in sys.path:
    sys.path.insert(0, PI_DIR)

from navigation_grid import decode_grid, encode_grid

with patch.dict(sys.modules, {
    "zmq": types.ModuleType("zmq"),
    "setproctitle": types.ModuleType("setproctitle"),
}):
    import boss


class NavigationGridTest(unittest.TestCase):
    def test_sparse_grid_round_trip_is_smaller_than_dense_grid(self):
        grid = [[0.0] * 21 for _ in range(21)]
        grid[1][2] = 0.25
        grid[20][20] = 1.0

        encoded = encode_grid(grid, 0.05, 10)
        decoded, resolution, origin = decode_grid(encoded)

        self.assertEqual(encoded["cells"], [[23, 25], [440, 100]])
        self.assertEqual(decoded, grid)
        self.assertEqual(resolution, 0.05)
        self.assertEqual(origin, 10)
        self.assertLess(len(json.dumps(encoded)), len(json.dumps(grid)))

    def test_rejects_malformed_sparse_grid(self):
        with self.assertRaises(ValueError):
            decode_grid({"width": 2, "height": 2, "cells": [[4, 100]], "resolution_m": 0.05, "origin_cell": 1})

    def test_boss_separates_pose_from_grid_snapshot(self):
        grid = [[0.0] * 3 for _ in range(3)]
        grid[1][2] = 1.0
        boss.p = types.SimpleNamespace(nav_state={
            "pose": {"x_m": 1.0, "y_m": 2.0, "heading_deg": 30.0},
            "motion": {"left_speed": 0.1, "right_speed": 0.1},
            "obstacles": {},
            "last_update_ts": "2026-11-13T12:00:00.000000",
            "grid": {
                "cells": grid,
                "size": 3,
                "preview_size": 3,
                "resolution_m": 0.05,
                "origin_cell": 1,
            },
        })

        pose = boss._build_snapshot_payload()
        sparse_grid = boss._build_grid_payload()

        self.assertNotIn("grid", pose)
        self.assertEqual(sparse_grid["cells"], [[5, 100]])


if __name__ == "__main__":
    unittest.main()