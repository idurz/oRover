#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  The BOSS server for the ROVER.
"""

#import signal
#import zmq # pyright: ignore[reportMissingImports]
import orover_lib as orover
import json
#import sys
#import uuid
import time
#import logging
#import serial
#from pythonjsonlogger.jsonlogger import JsonFormatter
#from datetime import datetime
#import boss_handler as handler
#import signal
from base_process import BaseProcess

# ---------------- CONFIG ----------------
#UART_PORT = "/dev/serial0"
#BAUDRATE = 115200
# ----------------------------------------

#config = orover.readConfig()
##logger = logging.getLogger()
#logger.setLevel(logging.INFO)
#logging.basicConfig(
#    format='%(asctime)s %(levelname)-8s %(message)s',
#    level=logging.INFO,
#    datefmt='%Y-%m-%d %H:%M:%S')
##logh = logging.FileHandler(config.get('boss','logfile',fallback="orover.log"))
#logh.setFormatter(JsonFormatter("{asctime} {message}", style="{"))
#logger.addHandler(logh)

#ser = serial.Serial(UART_PORT, BAUDRATE, timeout=1)

#try:
#    context = zmq.Context()
#    context.setsockopt(zmq.SNDTIMEO,config.getint('boss','send_timeout',fallback=2500))

#except Exception as e: 
#    sys.exit(f"Could not create ZMQ context. Exception {e}" )

#try:
##    socket = context.socket(zmq.REP)
#    socket.bind(config.get('boss','boss_socket',fallback='tcp://*:5555'))
#except Exception as e: 
#    sys.exit(f"Could not bind socket. Exception {e}" )

class boss_server(BaseProcess):
    def loop(self):
        while True:
            topicmsg = self.sub.recv_string()
            topic, msg = self.demogrify(topicmsg)
            print(f"topic = {topic}, BOSS: {msg}")
            err = handle_message(msg)
            print(f"handler: {err}")

def valid_uuid(id):
    try:
        uuid_object = uuid.UUID(id, version=4).hex
    except ValueError:
        return False
    return True


def valid_datetime(ts):
    try:
        date_object = datetime.strptime(ts,'%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
       return False
    return True


def valid_source(src):
    return src in orover.controller, orover.origin
   

def valid_priority(prio):
    return prio in orover.priority


def handle_message(m):

    # Check if valid json else discard
    try:
        message = json.loads(m.decode('utf-8'))
    except:
        return f"Discarding non-json message"
    
    # Check if all messages are present
    if not orover.all_fields_present(message, orover.KNOWN_FIELDS):
        return f"Field missing. Expecting all of {orover.KNOWN_FIELDS}" 

    if not valid_uuid(message['id']):
        return f"Discarding message; >>{message['id']}<< is not a valid UUID version 4"

    if not valid_datetime(message['ts']):
        return f"Discarding message {message['id']}: >>{message['ts']}<< is not a valid datetime in format '%Y-%m-%dT%H:%M:%S.%f'"
    
    if not valid_source(message['src']):
        return f"Discarding message {message['id']}: >>{message['src']}<< is not a valid origin"
    
    if not valid_priority(message['prio']):
        return f"Discarding message {message['id']}: >>{message['prio']}<< is not a valid priority"
    
    # No check on "me","pid","host","body"

    DISPATCH = {orover.event.object_detected:            handler.event_object_detected
               ,orover.cmd.shutdown:                     handler.cmd_shutdown
               ,orover.cmd.set_motor_speed:              handler.cmd_set_motor_speed
               }

    try:
        handler_routine = DISPATCH[message['reason']]
    except KeyError:
        return f"Discarding message {message['id']}: >>{message['reason']}<< is not a valid message reason!"
       
    result = handler_routine(message)
    logger.info("Request handled", extra = {"request" : message, "result" : result})
    return result


# Signal handler for graceful shutdown of child processes
#def terminate(signalNumber, frame):
##    global started_processes
#    print('Requested to stop')

    # requesting child processes to stop
#    for p in started_processes:
#        print(f"Terminating process {p['name']} with PID {p['process'].pid}")   
#        p["process"].terminate(signalNumber)
#    sys.exit()

class handler:
#""" Contains the handlers for BOSS messages """

    def event_object_detected(message):
        """ Handler for object detected events
            Parameters:
                message:   The standard message dictionary
                    body of message shoud contain parameter 'distance' 
                    with distance in cm (float)
            Returns:
                on error string with error description
                on success string "OK" 
        """
        sensor = orover.get_name(message.get('src'))
        body = message.get('body', {})
        if not "distance" in body:
            return f"message {message['id']} received without distance parameter in body"
       
        d = body.get('distance',0)
        # dummy action: print warning if object too close
        print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
        return "OK"
    
    def cmd_shutdown(socket,message,context, logger):
        """ Handler for shutdown command
            Parameters:
                    socket:    The ZMQ socket to send reply to
                    message:   The standard message dictionary
                        body of message may contain parameter 'value'
                        with reason for shutdown (string). If not present,
                        reason is 'unknown'
                    context:   The ZMQ context to terminate
                    logger:    The logger to log shutdown message
                Returns:
                    This handler does not return, it shuts down the server
                    However it sends an "OK" reply before shutting down
            """
        print(f"Shutdown message {message}")
        reason = message.get('body', {}).get('value', 'unknown')
        print(f"BOSS: Shutdown requested, reason: {reason}")
        socket.send(b"OK")
        socket.close(linger=2500)
        context.term()
        logger.info('Finished')
        exit(0)
    
    def cmd_set_motor_speed(message):
        """ Handler for object detected events
            Parameters:
                ser: serial port
                left_speed: left wheel speed
                right_speed: right wheel speedS
            Returns:
                on error string with error description
                on success string "OK" 
        """
        source = orover.get_name(message.get('src'))
        print(f"BOSS: in actuator_motor_wheels {source}")
        body = message.get('body', {})
        if not "left_speed" in body:
            return f"message {message['id']} received without left_speed parameter in body"
      
        return "OK"
    

if __name__ == "__main__":
    p = boss_server()
    p.loop()