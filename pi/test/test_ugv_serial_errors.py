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
    def test_run_loop_drains_bus_and_reads_available_serial_bytes(self):
        class Again(Exception):
            pass

        class FakeSub:
            def __init__(self):
                self.messages = ["cmd.set_motor_speed payload", "cmd.stop payload"]

            def recv_string(self, flags):
                if self.messages:
                    return self.messages.pop(0)
                raise Again

        class FakePoller:
            def __init__(self, sub):
                self.sub = sub

            def poll(self, timeout):
                return [(self.sub, 1)]

        base_module = types.ModuleType("base_process")
        base_module.baseprocess = type("FakeBase", (), {})
        serial_module = types.ModuleType("serial")
        zmq_module = types.ModuleType("zmq")
        zmq_module.Again = Again
        zmq_module.NOBLOCK = 1
        zmq_module.POLLIN = 1

        with patch.dict(sys.modules, {
            "base_process": base_module,
            "serial": serial_module,
            "zmq": zmq_module,
        }), patch.object(sys, "path", [PI_DIR] + sys.path):
            module = runpy.run_path(os.path.join(PI_DIR, "ugv.py"), run_name="ugv_test_module")

        process = module["base"].__new__(module["base"])
        process.running = True
        process.sub = FakeSub()
        process.poller = FakePoller(process.sub)
        process.fetchtopics = Mock()
        handled_messages = []

        def handle_message(topicmsg):
            handled_messages.append(topicmsg)
            if len(handled_messages) == 2:
                process.running = False

        process.handle_message = handle_message
        serial_port = Mock(in_waiting=4)
        serial_port.read.return_value = b"data"
        serial_handler = Mock()
        module["ugv"].serial_port = serial_port
        module["ugv"].handle_serial_input = serial_handler

        process.run()

        self.assertEqual(handled_messages, ["cmd.set_motor_speed payload", "cmd.stop payload"])
        serial_port.read.assert_called_once_with(4)
        serial_handler.assert_called_once_with(b"data")

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