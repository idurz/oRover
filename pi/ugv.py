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



class ugv_server(baseprocess):


    #def convert_to_serial(self, msg):
    #    return f"{msg['cmd']}\n".encode()


    #def convert_to_zmq(self, data):
    #    return {"raw": data.hex()}
    


    # zmq message handler, called when a message is received on the subscribed topic. 
    # Translates the message to a serial command and sends it to the UGV.
    def handle_message(self, message):

        #DISPATCH = {orover.event.object_detected:            handler.event_object_detected
        #           ,orover.cmd.shutdown:                     handler.cmd_shutdown
        #           ,orover.cmd.set_motor_speed:              handler.cmd_set_motor_speed
        #       }

        reason = message['reason']
        try:
            handler_routine = orover.DISPATCH[reason]
        except KeyError:
            u.logger.debug(f"Message discarded: {message['id']}: No handler for reason {u.enum_to_name(reason)} available in UGV server") 
            return
       
        serial_cmd = handler_routine(message)
        if serial_cmd is None:
            u.logger.debug(f"zmq message not correctly translated to serial output {message}, discarded")
            return          

        # write output to serial port, with locking to ensure thread safety. 
        # The handler routine is expected to return a bytes object that can be directly written to the serial port.
        u.serial.get_serial_lock.acquire()
        u.serial_port.write(serial_cmd)
        u.serial.get_serial_lock.release()
        
        return
    

    # zmq message handler, called when a message is received on the subscribed topic. Translates the message to a serial command and sends it to the UGV.
    def get_zmq(self):
        topicmsg = self.sub.recv()
        # retrieve the topic and message from the received zmq message, and validate the message structure and content
        _ , msg = self.demogrify(topicmsg)
        if self.valid_message(msg):
            self.handle_message(msg)
        else:
            u.logger.debug(f"Message discarded: {msg['id']}: Invalid message structure or content")
            return
    

    # Reads data from the serial port, converts it to a zmq message and publishes it on the bus.
    def get_serial(self):
        data = u.serial_port.read(1024)
        if data:
            msg = self.convert_to_zmq(data)
            self.pub.send_json(msg)



    # Loops indefinitely, checking for incoming zmq messages and serial data. Calls the appropriate handlers for each type of message.
    def run(self):
        while self.running:
            events = dict(self.poller.poll(timeout=10))
            if self.sub in events:
                self.get_zmq()
                topicmsg = self.sub.recv()

                # retrieve the topic and message from the received zmq message, and validate the message structure and content
                topic, msg = self.demogrify(topicmsg)
                if self.valid_message(msg):
                    self.handle_message(msg)
                
            # Check for serial data regardless of zmq events, to ensure we don't miss any incoming data
            self.get_serial()






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
