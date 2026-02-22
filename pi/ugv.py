#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  interface for UGV control (motor commands etc)
"""

from base_process import baseprocess
import oroverlib as orover
import serial
import time
import zmq
import json

class handler:
    """ Contains the handlers for UGV messages. Each handler takes a message as input and returns a result string. 
        The handlers are called by the UGV server when a message with the corresponding reason is received.
        Handlers do not return a response to the sender, but can perform actions based on the message content, 
        like logging or sending new messages to the bus.

        Each message is expected to have the following structure:

            "id"    : UUID
           ,"ts"    : datetime of message in '%Y-%m-%dT%H:%M:%S.%f' format
           ,"src"   : message source, e.g. specific sensor or actuator, should be in class origin
           ,"me"    : sending script name
           ,"host"  : sending node
           ,"prio"  : priority of message, should be in class priority
           ,"reason": type of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"body"  : JSON; contains parameters depending on type of message
    """

    # Wheel speed control  {"T":1,"L":<speed>,"R":<speed>} <speed> range -0.5 ~ +0.5 for right and left wheel. Unit m/s 

    # PWM motor control   {"T":11,"L":<range>,"R":<range>} <range> range -255 ~ +255. Suggested is to use this command only for debugging. For speed control you should use "Wheel speed control" above 

    # ROS Control         {"T":13,"X":<velocity>,"Z":<rad>} X is the velocity in m/s and the Z value is the steering angular velocity in rad/s. 

    # Setting Motor PID   {"T":2,"P":<val>,"I":<val>,"D":<val>,"L":<val>} The three values of P, I and D correspond to proportional, integral and differential coefficients respectively, and the value of L is the interface reserved for Windup Limits, which is not available for the default PID controller used in UGV01 at present, and we have reserved this interface to facilitate the replacement of other PID controllers by users. 

    # OLED Screen Setting {"T":3,"lineNum":<nr>,"Text":"putYourTextHere"} OLED screen display content settings, lineNum parameter for the line settings, can be: 0, 1, 2, 3, a total of 4 lines of content can be displayed. Each time you set a line of content, the new content will not affect the other lines of content displayed but will replace the original content before this line. The Text parameter is for the content setting where you can enter text that will be displayed on the corresponding line. After using this command, the OLED screen will not display the robot information, and display the content that the command lets it display. 

    # Restore OLED Screen {"T":-3} When the command type is -3, the OLED screen will be restored to the initial status, and the robot information will be displayed. 


    # Retrieve IMU Data {"T":126} Used to obtain IMU information, including heading angle, geomagnetic field, acceleration, attitude, temperature, etc.
    def cmd_getParam(message):
        # Retrieve IMU Data
        u.logger.debug(f"cmd_getParam -> {message}")
        return {"T":"126"}


    # Retrieve Chassis Information Feedback {"T":130,"cmd":<x>} Serial Port Continuous Feedback x=0 turn off (default),x=1 (turn on). When this function is not enabled, the chassis information feedback is realized through a question-and-answer method, and the above CMD_BASE_FEEDBACK and so on are used to get the chassis information feedback. When this function is enabled, the chassis can continuously feedback information, and not need to query through the host, suitable for the ROS system. 

    # Serial Port Echo Switch {"T":143,"cmd":<x>} <x>=0 off, <x>=1 on. When turned on, all the commands you send to the slave will appear in the serial port feedback. 

    # IO4 IO5 Control {"T":132,"IO4":<val>,"IO5":,<val>} For setting the PWM of IO4 and IO5. 

    # External Module Models {"T":4,"cmd":<x>} x=0: Null - 1: RoArm-M2 - 3: Gimbal 

    # Pan-tilt Control {"T":133,"X":45,"Y":45,"SPD":0,"ACC":0} If the product is installed with a pan-tilt, it can be controlled 



class ugv_server(baseprocess):

    # serial data handler, translates the serial data to a message and sends it to the bus
    def handle_serial(self, data):
        # This is a placeholder implementation, you should replace it with the actual parsing of your serial data
        # For example, if your serial data is in JSON format, you can do something like:
        try:
            msg = json.loads(data.decode())
        except Exception as e:
            u.logger.debug(f"Failed to parse serial data: {data} with exception {e}")   
            return None
        
        u.logger.debug(f"Serialized data {msg} but no handler implemented, returning None")  
        return None



    # zmq message handler, translates the message to a serial command and sends it to the UGV
    def handle_message(self, message):

        reason = message['reason']
        #try:
        handler_routine = orover.DISPATCH[reason]
        #except KeyError:
        #    u.logger.debug(f"Message discarded: {message['id']}: No handler for reason {u.enum_to_name(reason)} available in UGV server") 
        #    return
        serial_cmd = handler_routine(message)
        if serial_cmd is None:
            u.logger.debug(f"zmq message not correctly translated to serial output {message}, discarded")
            return          

        # write output to serial port, with locking to ensure thread safety. 
        u.serial.get_serial_lock.acquire()
        u.serial_port.write(serial_cmd)
        u.serial.get_serial_lock.release()
        return
    
       


    # Loops indefinitely, checking for incoming zmq messages and serial data. Calls the appropriate handlers for each type of message.
    def run(self):
        while self.running:
            events = dict(self.poller.poll(timeout=10))
            if self.sub in events:
                topicmsg = self.sub.recv()
                # retrieve the topic and message from the received zmq message, and validate the message structure and content
                _ , msg = self.demogrify(topicmsg)
                if self.valid_message(msg):
                    self.handle_message(msg)
                else:
                    u.logger.debug(f"Message discarded: {msg['id']}: Invalid message structure or content")
                    return
                
            # Check for serial data regardless of zmq events, to ensure we don't miss any incoming data
            data = u.serial_port.read(1024)
            if data:
                u.logger.debug(f"Received serial data: {data}")
                msg = self.handle_serial(data)
                if msg:
                    u.logger.debug(f"Publishing message from serial data: {msg}")  
                self.pub.send_json(msg)


# ---------------- CONFIG ----------------
LINEAR_SPEED = 0.3     # m/s (tune this)
ANGULAR_SPEED = 45.0   # deg/s (tune this)

CMD_PERIOD = 0.1       # seconds (10 Hz, keeps watchdog alive)
# ----------------------------------------

def send_cmd(ser, left, right):
    cmd = f'{{"T":1,"L":{left:.2f},"R":{right:.2f}}}\n'
    with ser_lock:
        ser.write(cmd.encode())

def stop(ser):
    with ser_lock:
        send_cmd(ser, 0.0, 0.0)

def drive_straight(ser, distance):
    direction = 1.0 if distance >= 0 else -1.0
    duration = abs(distance) / LINEAR_SPEED

    left = 0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        with ser_lock:
            send_cmd(ser, left, right)
            time.sleep(CMD_PERIOD)

    stop(ser)

def rotate(ser, angle_deg):
    direction = 1.0 if angle_deg >= 0 else -1.0
    duration = abs(angle_deg) / ANGULAR_SPEED

    # In-place rotation
    left = -0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        with ser_lock:
            send_cmd(ser, left, right)
            time.sleep(CMD_PERIOD)

    stop(ser)



#### Main execution starts here ####
if __name__ == "__main__":
    u = ugv_server()

    serial_dev = u.config.get("serial", "port", fallback="/dev/ttyUSB0")
    serial_baud = u.config.getint("serial", "baudrate", fallback=115200)

    u.serial_port = serial.Serial(serial_dev, baudrate=serial_baud, timeout=0)

    u.poller = zmq.Poller()
    u.poller.register(u.sub, zmq.POLLIN)

    u.run()
