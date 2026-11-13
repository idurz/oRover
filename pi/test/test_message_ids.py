#!/usr/bin/env python3

import os
import sys
import types
import unittest
import uuid
import base64
from unittest.mock import patch


PI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PI_DIR not in sys.path:
    sys.path.insert(0, PI_DIR)

with patch.dict(sys.modules, {
    "zmq": types.ModuleType("zmq"),
    "setproctitle": types.ModuleType("setproctitle"),
}):
    from base_process import baseprocess, new_message_id


class MessageIdTest(unittest.TestCase):
    def setUp(self):
        self.process = baseprocess.__new__(baseprocess)

    def test_generated_id_is_compact_base64url_uuid(self):
        message_id = new_message_id()

        self.assertEqual(len(message_id), 22)
        self.assertTrue(self.process.valid_uuid(message_id))

    def test_accepts_legacy_uuid4(self):
        self.assertTrue(self.process.valid_uuid(str(uuid.uuid4())))

    def test_accepts_epoch_milliseconds_and_legacy_timestamp(self):
        self.assertTrue(self.process.valid_datetime(1_775_651_696_123))
        self.assertTrue(self.process.valid_datetime("2026-04-08T12:34:56.123456"))
        self.assertFalse(self.process.valid_datetime("not-a-timestamp"))
        self.assertFalse(self.process.valid_datetime(True))

    def test_rejects_malformed_ids(self):
        self.assertFalse(self.process.valid_uuid("not-a-uuid"))
        self.assertFalse(self.process.valid_uuid("=" * 22))
        non_v4_id = base64.urlsafe_b64encode(bytes(16)).rstrip(b"=").decode("ascii")
        self.assertFalse(self.process.valid_uuid(non_v4_id))


if __name__ == "__main__":
    unittest.main()