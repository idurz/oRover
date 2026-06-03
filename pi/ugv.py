#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  interface for UGV control (motor commands etc)
"""
import oroverlib as orover
from base_process import baseprocess
import serial
import time
import zmq
import json
import threading


# todo: 2026-04-14 22:08:42 ugv      DEBUG     - Received serial data: b'{"T": 1, "L": 0.5, "R": 0.5}\n'
#2026-04-14 22:08:42 ugv      DEBUG     - serial_data_received -> {'T': 1, 'L': 0.5, 'R': 0.5}
#2026-04-14 22:08:42 ugv      DEBUG     - Received serial data with unrecognized format: {'T': 1, 'L': 0.5, 'R': 0.5}, returning False


class handler:
    """ Contains the handlers for UGV messages. Each handler takes a message as input and returns a result string. 
        The handlers are called by the UGV server when a message with the corresponding reason is received.
        Handlers do not return a response to the sender, but can perform actions based on the message content, 
        like logging or sending new messages to the bus.
    """
    def __init__(self):
        self.ismoving = False # Checks if robot is currently moving, to prevent sending multiple movement commands at the same time. 
        #self.routetogo = None # Stores the current route to follow for moveTo commands, which can be used to implement obstacle avoidance or dynamic path replanning in the future.
    
    def _route_check(self, route):
        # Check if route is valid, meaning it is a list of segments with valid distance and angle parameters. 
        if not isinstance(route, list) or not route:
            return False
        for step in route:
            if not isinstance(step, dict):
                return False
            if "distance" not in step and "angle" not in step:
                b.logger.error(f"Route step {step} is missing distance or angle parameter") 
                return False
            if "distance" in step and not isinstance(step["distance"], (int, float)):
                b.logger.error(f"Route step {step} has invalid distance parameter")
                return False
            if "angle" in step and not isinstance(step["angle"], (int, float)):
                b.logger.error(f"Route step {step} has invalid angle parameter")
                return False
        return True

    def _start_motion(self, *args, **kwargs):
        self.ismoving = True
        self.mv_thread = threading.Thread(target=ugv.move_rover_thread, args=args, kwargs=kwargs, daemon=True)
        self.mv_thread.start()

    def cmd_move(self,message):
        # Handle move command, expects body to contain "left_speed" and "right_speed" parameters, 
        # which are the speeds for the left and right wheels in m/s. This action will nog stop until 
        # a stop command is received, or another move command is received while already moving. 
        # 
        # A move is a route with one segment with the given speeds, and no distance or angle limit. 
        # The robot should keep sending motor commands
        route = None
        if self.ismoving:
            b.logger.warning("cmd_move ignored: robot is already moving")
            return False
        body = message.get('body') or {}
        if "left_speed" not in body:
            b.logger.warning(f"cmd_move received without left_speed parameter in body, defaulting to 0")
            left_speed = self.linear_speed
        else:
            left_speed = body.get('left_speed')
        if "right_speed" not in body:
            b.logger.warning(f"cmd_move received without right_speed parameter in body, defaulting to 0")
            right_speed = self.linear_speed
        else:
            right_speed = body.get('right_speed')  
        route = [{"left_speed": left_speed, "right_speed": right_speed, "distance": None, "angle": None}]
        b.logger.debug(f"cmd_move starting motion with route {route}")
        self._start_motion(route)

    def cmd_moveTo(self,message):
        # Handle moveTo command, expects body to contain "distance" and "angle" parameters, which are the distance in meters 
        # and angle in degrees to move relative to current position. The robot should calculate the required wheel speeds 
        # and durations to achieve the desired movement, and send the appropriate motor commands to the serial port. 
        # 
        # A moveTo is a route with one segment with the given distance and angle, and default speeds. 
        route = None
        if self.ismoving:
            b.logger.warning("cmd_moveTo ignored: robot is already moving")
            return False
        body = message.get('body') or {}

        # check for distance and angle parameters in body, and use default values if not provided
        if "distance" not in body:
            b.logger.warning(f"cmd_moveTo received without distance parameter in body, defaulting to 0")
            distance = 0
        else:
            distance = body.get('distance')

        if "angle" not in body:
            b.logger.warning(f"cmd_moveTo received without angle parameter in body, defaulting to 0")
            angle = 0
        else:
            angle = body.get('angle')

        route = [{"distance": distance, "angle": angle}]
        b.logger.debug(f"cmd_moveTo starting motion with route {route}")
        self._start_motion(route)

    def cmd_moveRoute(self, message):
        # Handle route command, expects body to contain a route list with distance/angle steps.
        print(f"cmd_moveRoute received with message {message}")
        if self.ismoving:
            b.logger.warning("cmd_moveRoute ignored: robot is already moving")
            return False
        body = message.get('body') or {}
        if "id" not in body:
            b.logger.warning(f"cmd_moveRoute received without id parameter in body, defaulting to unknown")
            route_id = "unknown"
        else:
            route_id = body.get("id")

        route = body.get("route") or []
        if not isinstance(route, list) or not route:
            b.logger.warning(f"cmd_moveRoute ignored: route {route_id} has invalid or empty route in message {message.get('id')}")
            return False
        if not self._route_check(route):
            b.logger.warning(f"cmd_moveRoute ignored: route {route_id} contains invalid steps in message {message.get('id')}")
            return False
        
        b.logger.debug(f"cmd_moveRoute id {route_id} starting motion with route {route}")
        self._start_motion(route)

    def event_obstacleDetected(self, message):
        # Handle obstacle detected event, expects body to contain "distance" and "angle" parameters, which are the distance 
        # in meters and angle in degrees to the detected obstacle relative to the robot. 
        if not self.ismoving:
            b.logger.warning("event_obstacleDetected received but robot is not moving, ignoring")
            return False
        body = message.get('body') or {}
        distance = body.get('distance')
        angle = body.get('angle')
        b.logger.info(f"Obstacle detected at distance {distance} m and angle {angle} deg, NO ACTION TAKEN (obstacle avoidance not implemented yet)")
        return True

    def cmd_getParam(self,message):
        # Retrieve IMU Data {"T":126} Used to obtain IMU information, including heading angle, geomagnetic field, acceleration, attitude, temperature, etc.
        b.logger.debug(f"cmd_getParam -> {message}")
        s = json.dumps({"T":"126"})
        ugv.write_serial(s)

    def cmd_setParam(self,message):
        # Retrieve IMU Data
        b.logger.debug(f"cmd_setParam -> {message}")
        s = json.dumps({"T":3,"lineNum":2,"Text":"Rudi"})
        ugv.write_serial(s)

    def cmd_set_motor_speed(self, message):
        # Handle motor speed command
        b.logger.debug(f"cmd_set_motor_speed -> {message}") #{"T":1,"L":,"R":}
        body = message.get('body', {})
        if not "left_speed" in body or not "right_speed" in body:
            b.logger.warning(f"Message {message['id']} received without left_speed or right_speed parameter in body")
            return False
        # body={"left_speed": left_speed, "right_speed": right_speed})
        s = json.dumps({"T":1,"L":body.get("left_speed"),"R":body.get("right_speed")})
        # set this speed as default for move and moveTo commands, until another speed command is received
        ugv.linear_speed = body.get("left_speed")
        ugv.angular_speed = body.get("right_speed")
        ugv.write_serial(s)


class ugv:
    """ CHandler class for UGV messages, received via serial port. The handler functions parse the incoming serial data, 
        extract relevant information, and send new messages to the bus based on the content of the serial data. 
    """
    def __init__(self):
        self.linear_speed = b.config.getfloat("ugv", "linear_speed", fallback=0.5) # Default linear speed in m/s
        self.angular_speed = b.config.getfloat("ugv", "angular_speed", fallback=90.0) # Default angular speed in degrees/s
        self.cmd_period = b.config.getfloat("ugv", "cmd_period", fallback=0.1) # Default command period in seconds
        self._serial_rx_buffer = ""

        # ESP feedback type map from firmware json_cmd.h.
        self._serial_type_name = {
            1001: "base_feedback",
            1002: "imu_feedback",
            1003: "esp_now_recv",
            1004: "esp_now_send_status",
            1005: "servo_bus_status",
            1051: "roarm_feedback",
            139: "speed_rate_feedback",
        }

    def open_serial(self):
        # Open the serial port for communication with the UGV, using the configuration parameters from the config file
        serial_dev = b.config.get("serial", "port", fallback="/dev/ttyUSB0")
        serial_baud = b.config.getint("serial", "baudrate", fallback=115200)
        serial_timeout = b.config.getfloat("serial", "timeout", fallback=0.1)
        b.logger.info(f"Opening serial port {serial_dev} with baudrate {serial_baud}")
        self.serial_port = serial.Serial(serial_dev, baudrate=serial_baud, timeout=serial_timeout)

    def close_serial(self):
        # Ensure serial port is closed on exit
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            b.logger.info("Serial port closed")

    def handle_serial_input(self, data):
        # ESP serial output is newline-delimited. Buffer chunks to handle partial/multiple frames.
        try:
            chunk = data.decode("utf-8", errors="replace")
        except Exception as e:
            b.logger.error(f"Serial data decode failed for {data!r}: {e}")
            return

        self._serial_rx_buffer += chunk

        while "\n" in self._serial_rx_buffer:
            line, self._serial_rx_buffer = self._serial_rx_buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            self._handle_serial_line(line)

    def _handle_serial_line(self, line):
        # Normalize each serial line into: typed_json / json_untyped / text.
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            b.logger.debug(f"serial_text_received -> {line}")
            return

        if not isinstance(msg, dict):
            b.logger.debug(f"serial_json_untyped_received -> {msg}")
            return

        msg_type = msg.get("T")
        if isinstance(msg_type, int):
            self._handle_typed_serial_message(msg_type, msg)
            return

        b.logger.debug(f"serial_json_untyped_received -> {json.dumps(msg)}")
        self._handle_untyped_serial_message(msg)

    def _handle_untyped_serial_message(self, msg):
        channel = "serial_json_untyped"
        if any(k in msg for k in ("ip", "rssi", "wifi_mode_on_boot", "sta_ssid", "ap_ssid")):
            channel = "wifi_status"
        elif any(k in msg for k in ("info", "mac", "status", "message", "megs")):
            channel = "system_status"

        b.send_event(
            src=orover.origin.orover_ugv,
            reason=orover.state.sensor_status,
            body={
                "channel": channel,
                "payload": msg,
            },
        )

    def _handle_typed_serial_message(self, msg_type, msg):
        msg_name = self._serial_type_name.get(msg_type, "unknown_typed_json")
        b.logger.debug(f"serial_typed_received -> T={msg_type} ({msg_name}) payload={json.dumps(msg)}")

        # Keep dispatch explicit so it is easy to map firmware changes.
        if msg_type == 1001:
            b.logger.debug("serial_dispatch -> base feedback")
            b.send_event(
                src=orover.origin.sensor_battery,
                reason=orover.state.battery,
                body={"voltage": msg.get("v")},
            )
            b.send_event(
                src=orover.origin.sensor_imu,
                reason=orover.state.motion,
                body={
                    "heading": msg.get("r"),
                    "roll": msg.get("y"),
                    "left_speed": msg.get("L"),
                    "right_speed": msg.get("R"),
                    "pitch": msg.get("p"),
                    "temperature": msg.get("temp"),
                },
            )
        elif msg_type == 1002:
            b.logger.debug("serial_dispatch -> imu feedback")
            b.send_event(
                src=orover.origin.sensor_imu,
                reason=orover.state.motion,
                body={
                    "heading": msg.get("r"),
                    "roll": msg.get("y"),
                    "pitch": msg.get("p"),
                    "ax": msg.get("ax"),
                    "ay": msg.get("ay"),
                    "az": msg.get("az"),
                    "gx": msg.get("gx"),
                    "gy": msg.get("gy"),
                    "gz": msg.get("gz"),
                    "mx": msg.get("mx"),
                    "my": msg.get("my"),
                    "mz": msg.get("mz"),
                    "temperature": msg.get("temp"),
                },
            )
        elif msg_type == 1003:
            b.logger.debug("serial_dispatch -> esp-now receive")
            b.send_event(
                src=orover.origin.orover_ugv,
                reason=orover.state.sensor_status,
                body={
                    "channel": "esp_now_recv",
                    "mac": msg.get("mac"),
                    "message": msg.get("megs"),
                },
            )
        elif msg_type == 1004:
            b.logger.debug("serial_dispatch -> esp-now send status")
            b.send_event(
                src=orover.origin.orover_ugv,
                reason=orover.state.sensor_status,
                body={
                    "channel": "esp_now_send",
                    "mac": msg.get("mac"),
                    "status": msg.get("status"),
                    "message": msg.get("megs"),
                },
            )
        elif msg_type == 1005:
            b.logger.debug("serial_dispatch -> servo bus status")
            b.send_event(
                src=orover.origin.orover_ugv,
                reason=orover.state.sensor_status,
                body={
                    "channel": "servo_bus",
                    "id": msg.get("id"),
                    "status": msg.get("status"),
                },
            )
        elif msg_type == 1051:
            b.logger.debug("serial_dispatch -> roarm feedback")
            b.send_event(
                src=orover.origin.orover_ugv,
                reason=orover.state.pose,
                body={
                    "x": msg.get("x"),
                    "y": msg.get("y"),
                    "z": msg.get("z"),
                    "b": msg.get("b"),
                    "s": msg.get("s"),
                    "e": msg.get("e"),
                    "t": msg.get("t"),
                    "torB": msg.get("torB"),
                    "torS": msg.get("torS"),
                    "torE": msg.get("torE"),
                    "torH": msg.get("torH"),
                },
            )
        elif msg_type == 139:
            b.logger.debug("serial_dispatch -> speed rate feedback")
            b.send_event(
                src=orover.origin.orover_ugv,
                reason=orover.state.actuator_speed,
                body={
                    "left_rate": msg.get("L"),
                    "right_rate": msg.get("R"),
                },
            )
        else:
            b.logger.debug(f"serial_dispatch -> unknown typed message T={msg_type}")

    def write_serial(self,serialmsg):
        if serialmsg:
            s = f"{serialmsg}\n"
            b.logger.debug(f"Writing to serial port: {s}")
            ugv.serial_port.write(s.encode())

    def _move_segment(self, left_speed = 0, right_speed = 0, distance=None, angle=None):
        b.logger.debug(f"_move_segment called with left_speed={left_speed}, right_speed={right_speed},   angle={angle}, distance={distance}")
    
        if distance is not None:
            # Drive straight for a calculated duration based on LINEAR_SPEED
            direction = 1.0 if distance >= 0 else -1.0
            duration = abs(distance) / self.linear_speed
            start = time.time()
            while time.time() - start < duration:
                b.logger.debug(f"Moving straight for distance {distance} m at speed {self.linear_speed} m/s, duration {duration:.2f} s; time elapsed {time.time() - start:.2f} s")
                self._write(left_speed * direction, right_speed * direction)
                time.sleep(self.cmd_period)
        
        if angle is not None:
            # Rotate in-place for a calculated duration based on ANGULAR_SPEED
            direction = 1.0 if angle >= 0 else -1.0
            duration = abs(angle) / self.angular_speed
            start = time.time()
            while time.time() - start < duration:
                b.logger.debug(f"Rotating in-place for angle {angle} deg at speed {self.angular_speed} deg/s, duration {duration:.2f} s; time elapsed {time.time() - start:.2f} s")
                self._write(-left_speed * direction, right_speed * direction)
                time.sleep(self.cmd_period)
        
        if distance is None and angle is None:
            # No distance or angle limit, keep sending the same speed command until another command is received or stop command is received.
            b.logger.debug(f"Moving with left_speed={left_speed} and right_speed={right_speed} indefinitely until next command")
            while self.ismoving:
                #self._write(left_speed, right_speed)
                time.sleep(self.cmd_period)
                
    def move_rover_thread(self,route):
        # This function calculates the required motor commands to move the robot forward with the given speeds, 
        # and optionally rotate by a certain angle or move a certain distance. If angle or distance is provided, 
        # the function calculates the required duration for the movement and send the appropriate (multiple) motor commands
        # a route is a list of segments, where each segment has a distance and angle to move, and the robot should execute them sequentially.
        b.logger.debug(f"move_rover_thread called with route={route}")
        for step in route or []:
            if not h.ismoving:
                b.logger.debug("move_rover_thread stopping early because ismoving was cleared")
                break
            if "left_speed" not in step:
                step["left_speed"] = self.linear_speed
            if "right_speed" not in step:
                step["right_speed"] = self.linear_speed
            if "distance" not in step:
                step["distance"] = None
            if "angle" not in step:                   
                step["angle"] = None
            self._move_segment(step.get("left_speed"), step.get("right_speed"), step.get("distance"), step.get("angle"))
        self._stop()

    def _write(self, left, right):
        cmd = json.dumps({"T": 1, "L": round(left, 2), "R": round(right, 2)}) + "\n"
        self.serial_port.write(cmd.encode())

    def _stop(self):
        self._write(0.0, 0.0)
        h.ismoving = False
    

class base(baseprocess):
    """ Base class for the UGV server, contains the main loop to receive messages from the bus and handle them, 
        as well as the serial data handling logic. We need to overwrite run() to implement the main loop, and 
        handle_serial() to process incoming serial data. The base class provides the infrastructure for message 
        handling and communication with the bus, while the handler class contains the specific logic for handling UGV-related messages.
    """
    def run(self):
        # Main loop to receive messages from the bus and handle them, runs until termination signal is received
        self.fetchtopics() # Fetch the topics and handlers before starting the main loop
        while self.running:
            # read topic and message from the SUB socket, then handle the message
            events = dict(self.poller.poll(timeout=10))
            if self.sub in events:
                topicmsg = self.sub.recv_string()
                self.handle_message(topicmsg)

            # Check for serial data regardless of zmq events, to ensure we don't miss any incoming data
            data = ugv.serial_port.read(1024)
            if data:
                ugv.handle_serial_input(data)


#### Main execution starts here ####
if __name__ == "__main__":
    h = handler() # Instantiate the handler class, which contains the message handlers for the BOSS server
    b = base(handler=h,threadingsubsocket=False) # Instantiate the base class, which contains the main loop and message handling logic for the BOSS server
    ugv = ugv() # Instantiate the UGV class, which contains the logic for handling serial data and sending motor commands
    ugv.open_serial() # Open the serial port for communication with the UGV, using the configuration parameters from the config file

    b.poller = zmq.Poller()
    b.poller.register(b.sub, zmq.POLLIN)

    try:
        b.run()
    finally:
        ugv.close_serial()