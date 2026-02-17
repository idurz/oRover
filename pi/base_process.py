#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  base process class for all rover processes, providing common functionality like event handling and heartbeat
"""

import datetime
import json
import os
import signal
import sys
import zmq
import time
import uuid
import threading
import logging, logging.handlers
import oroverlib as orover
import setproctitle


# Base class for all processes, providing common functionality like event handling and heartbeat
class baseprocess:
    def __init__(self):

        self.config = orover.readConfig()  # Read configuration from config.ini file
        self.myname = orover.getmodulename(self.config)  # Get the name of the current script for use in messages
        self.logger = orover.setlogger(self.config)
        setproctitle.setproctitle(f"orover:{orover.getmodulename(self.config)}")

        # Create ZMQ context and sockets for communication with the boss process and event bus
        self.ctx = zmq.Context()

        # Create zmq PUB socket for event bus, connect to port
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.connect(self.config.get("eventbus","client_pub_socket",fallback="tcp://localhost:5556"))
    
        # Create zmq SUB socket for event bus, bind to port
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(self.config.get("eventbus","client_sub_socket",fallback="tcp://localhost:5555"))
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Start done, register signal handler for graceful shutdown and log the start of the process
        signal.signal(signal.SIGTERM, self.terminate)
        self.running = True
        self.logger.info(f"{self.myname} started with PID {os.getpid()}")

        # is heart_beat_interval configured? If so, start the heartbeat thread
        self.heart_beart_interval = self.config.getint('orover','heartbeat_interval',fallback=0)
        if self.heart_beart_interval > 0:
            self.logger.info(f"Starting heartbeat thread with interval {self.heart_beart_interval} seconds")
            self.hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.hb_thread.start()




    # Return the best-effort name for a numeric type.
    def enum_to_name(self, val) -> str:
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
            try:
                return f"{cls(val).__class__.__name__}.{cls(val).name}"
            except ValueError:
                pass
        return f"{cls(val).__class__.__name__}.unknown({val})"



    # Return the best-effort number based on a name 
    def name_to_enum(self, name):
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
            try:
                return cls[name]
            except KeyError:
                pass
        return None




    # Signal handler for graceful shutdown of myself and child processes
    def terminate(self,signalNumber, frame):
        self.pub.close()
        self.sub.close()
        self.ctx.term()
        self.running = False
        sys.exit()




    # json encode the message and prepend the topic
    #def mogrify(self, topic, msg):
    #    return topic + ' ' + json.dumps(msg)

    # Return the topic and JSON decoded message from the topic+message string received from the bus
    def demogrify(self, topicmsg):
        json0 = topicmsg.find('{')
        topic = topicmsg[0:json0].strip()
        msg = json.loads(topicmsg[json0:])
        return topic, msg
    



    # Publish an event to the bus, with validation of fields and JSON body
    def send_event(self, src, reason,body={}, prio=None):
        self.logger.debug(f"Preparing to send event with src {src}, reason {reason}, body {body} and prio {prio}")

        if not isinstance (src,(orover.origin, orover.actuator, orover.controller)):
            self.logger.error(f"Invalid 'src' field, must be known enum ({src})")
            return False
    
        if not isinstance(reason, (orover.cmd, orover.state, orover.event)):
            self.logger.error(f"Invalid 'reason' field must be known enum ({reason})")
            return False

        # check if body is valid json
        body_field = body
        if isinstance(body, str):
            try:
                body_field = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                self.logger.error(f"{body} is not valid JSON")
                return False

        # priority: accept an int or Priority member
        if prio is None:
            prio = orover.priority.normal
            if not isinstance(prio,orover.priority):
                self.logger.error(f"Invalid 'prio' field must be known enum ({prio})")
                return False    


        # Construct the message to send to the boss
        msg = {"id"  : str(uuid.uuid4())
              ,"ts"  : datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
              ,"src" : src
              ,"me"  : self.myname
              ,"host": os.uname().nodename
              ,"prio": prio
              ,"reason": reason
              ,"body": body_field
              } 

        # create the topic string and JSON encode the message, then send to the bus
        msgstring = self.enum_to_name(reason) + ' ' + json.dumps(msg)
        self.logger.debug(f"Sending event {json.dumps(msg)}")

        try:
            self.pub.send_string(msgstring)
        except Exception as e: 
            self.logger.error(f"Publishing ZMQ message failed with exception {e}") 
            return False

        return True




    # Heartbeat loop, sending a heartbeat event at the configured interval
    def _heartbeat_loop(self):
        while self.running:
            self.send_event(src=orover.origin.heartbeat
                           ,reason=orover.event.heartbeat
                           ,body={})
            time.sleep(self.heart_beart_interval)


    # test method to validate if all fields are present in the message
    def all_fields_present(self, message):
        """ "id"    : UUID
           ,"ts"    : datetime of message in '%Y-%m-%dT%H:%M:%S.%f' format
           ,"src"   : message source, e.g. specific sensor or actuator, should be in class origin
           ,"me"    : sending script name
           ,"host"  : sending node
           ,"prio"  : priority of message, should be in class priority
           ,"reason": type of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"body"  : contains parameters depending on type of message
        """
        for s in ["id","ts","src","me","host","prio","reason","body"]:
            afp = (s in message)
            if not afp:
                break
            return afp
        



    # test method to validate uuid
    def valid_uuid(self, id):
        try:
            uuid_object = uuid.UUID(id, version=4).hex
        except ValueError:
            return False
        return True




    # test method to validate datetime
    def valid_datetime(self, ts):
        try:
            date_object = datetime.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            return False
        return True




    # test method to validate source
    def valid_source(self, src):
        return src in orover.controller, orover.origin
   



    # test method to validate priority
    def valid_priority(self,prio):
        return prio in orover.priority




    # Check if the message has the required fields and valid values, return True if valid, False otherwise
    def valid_message(self, msg):
        
        if not self.all_fields_present(msg):
            self.logger.error(f"Discarding message {msg} --> Field missing in message")
            return False
        if not self.valid_uuid(msg['id']):
            self.logger.error(f"Discarding message {msg} --> {msg['id']}<< is not a valid UUID version 4")
            return False
        if not self.valid_datetime(msg['ts']):
            self.logger.error(f"Discarding message {msg['id']}: >>{msg['ts']}<< is not a valid datetime in format '%Y-%m-%dT%H:%M:%S.%f'")
            return False
        if not self.valid_source(msg['src']):
            self.logger.error(f"Discarding message {msg['id']}: >>{msg['src']}<< is not a valid origin")
            return False
        if not self.valid_priority(msg['prio']):
            self.logger.error(f"Discarding message {msg['id']}: >>{msg['prio']}<< is not a valid priority")
            return False
        self.logger.debug(f"Validated message {msg}")
        return True




    # Override this method in child classes to handle incoming messages from the bus
    def handle_message(self, msg):
        pass




    # Main loop to receive messages from the bus and handle them, runs until termination signal is received
    def run(self):
        while self.running:
            # read topic and message from the SUB socket, then handle the message
            topicmsg = self.sub.recv_string()
            _ , msg = self.demogrify(topicmsg)

            if self.valid_message(msg):
                self.handle_message(msg)