#!/usr/bin/env python3

import contextlib
import io
import os
import runpy
import sys
import types
import unittest
from unittest.mock import Mock, patch


PI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UgvSerialErrorTest(unittest.TestCase):
    def run_with_serial_failure(self, failure_stage):
        serial_module = types.ModuleType("serial")
        serial_module.SerialException = type("SerialException", (OSError,), {})
        serial_port = Mock(is_open=True)
        error = serial_module.SerialException("Permission denied: /dev/serial0")
        serial_module.Serial = Mock(return_value=serial_port)
        if failure_stage == "open":
            serial_module.Serial.side_effect = error
        else:
            serial_port.read.side_effect = error
        logger = Mock()
        config = Mock()
        config.get.side_effect = lambda section, option, fallback: "/dev/serial0"
        config.getint.side_effect = lambda section, option, fallback: 0 if option == "ugv_updates_interval" else fallback
        config.getfloat.side_effect = lambda section, option, fallback: fallback
        config.getboolean.side_effect = lambda section, option, fallback: fallback

        instances = []

        class FakeBase:
            def __init__(self, **kwargs):
                self.config = config
                self.logger = logger
                self.running = True
                self.sub = object()
                self.fetchtopics = Mock()
                instances.append(self)

        base_module = types.ModuleType("base_process")
        base_module.baseprocess = FakeBase
        zmq_module = Mock()
        zmq_module.Poller.return_value.poll.return_value = []
        modules = {"base_process": base_module, "serial": serial_module, "zmq": zmq_module}
        stderr = io.StringIO()
        with patch.dict(sys.modules, modules), patch.object(sys, "path", [PI_DIR] + sys.path), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(os.path.join(PI_DIR, "ugv.py"), run_name="__main__")

        self.assertEqual(result.exception.code, 1)
        self.assertIn("UGV serial communication failed: Permission denied: /dev/serial0", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
        logger.error.assert_called_once_with("UGV serial communication failed: Permission denied: /dev/serial0")
        self.assertFalse(instances[0].running)
        return serial_port

    def test_serial_open_failure_is_reported_without_traceback(self):
        serial_port = self.run_with_serial_failure("open")
        serial_port.close.assert_not_called()

    def test_serial_read_failure_closes_port(self):
        serial_port = self.run_with_serial_failure("read")
        serial_port.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()