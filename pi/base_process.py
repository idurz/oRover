#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  base process class for all rover processes, providing common functionality like event handling and heartbeat
"""

import argparse
import configparser
import datetime
import json
import os
import signal
import sys
import zmq
import time
import uuid
import threading
import logging
from pythonjsonlogger.jsonlogger import JsonFormatter
import orover_lib as orover


class BaseProcess:
    def __init__(self):
        # Check if config file is given as argument, otherwise use default
        self.parser = argparse.ArgumentParser(description="oRover startup script"
                                             ,prog="python3 base_process.py")
        self.parser.add_argument("--config"
                                ,type=str
                                ,required=False
                                ,default="config.ini"
                                ,help="Path to configuration file (default: config.ini)")  
        self.args = self.parser.parse_args()

        # Read configuration from config.ini file
          
        if not os.path.isfile(self.args.config):
            sys.exit(f"Configuration file {self.args.config} does not exist")        

        self.config = configparser.ConfigParser() 
        self.config.read(self.args.config)

        # Create zmq PUB socket for event bus, bind to port
        #subbadress = self.config.get("orover","subscribe_socket",fallback="tcp://localhost:5555")
        #pubbadress = self.config.get("orover","publish_socket",fallback="tcp://*:5555")

        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.connect("tcp://localhost:5556")
    
        # Create zmq SUB socket for event bus, bind to port
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5555")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Start done, register signal handler for graceful shutdown
        signal.signal(signal.SIGTERM, self.terminate)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        logh = logging.FileHandler(self.config.get('boss','logfile',fallback="orover.log"))
        logh.setFormatter(JsonFormatter("{asctime} {message}", style="{"))
        self.logger.addHandler(logh)
        
        self.running = True

        self.hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.hb_thread.start()


    # Return the best-effort name for a numeric type.
    def get_name(self, val) -> str:
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
    
        #     print(f"Trying to get name for {val} from {cls}")   
        #     try:
        #         return f"{str(cls.name)} found {cls(val).name}"
        #     except Exception:
        #         pass
        # print(f"Could not get name for value {val}, returning string representation")
        # return str(val)  
            try:
                return f"{cls(val).__class__.__name__}.{cls(val).name}"
            except ValueError:
                pass
        return f"{cls(val).__class__.__name__}.unknown({val})"



    # Signal handler for graceful shutdown of myself and child processes
    def terminate(self,signalNumber, frame):
        self.pub.close()
        self.sub.close()
        self.context.term()
        sys.exit()

    def mogrify(self, topic, msg):
        """ json encode the message and prepend the topic """
        return topic + ' ' + json.dumps(msg)

    def demogrify(self, topicmsg):
        """ Inverse of mogrify() """
        json0 = topicmsg.find('{')
        topic = topicmsg[0:json0].strip()
        msg = json.loads(topicmsg[json0:])
        return topic, msg
    
    # Publish an event to the bus, with validation of fields and JSON body
    def send_event(self, src, reason,body={}, prio=None):
        print(f"Preparing to send event with src {src}, reason {reason}, body {body} and prio {prio}")

        if not isinstance (src,(orover.origin, orover.actuator, orover.controller)):
            print (f"Invalid 'src' field, must be known enum ({src})")
            return False
    
        if not isinstance(reason, (orover.cmd, orover.state, orover.event)):
            print (f"Invalid 'reason' field must be known enum ({reason})")
            return False

        # check if body is valid json
        body_field = body
        if isinstance(body, str):
            try:
                body_field = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                print (f"{body} is not valid JSON")
                return False

        # priority: accept an int or Priority member
        if prio is None:
            prio = orover.priority.normal
            if not isinstance(prio,orover.priority):
                print (f"Invalid 'prio' field must be known enum ({prio})")
                return False    


        # Construct the message to send to the boss
        msg = {"id"  : str(uuid.uuid4())
              ,"ts"  : datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
              ,"src" : src
              ,"me"  : sys.argv[0]
              ,"host": os.uname().nodename
              ,"prio": prio
              ,"reason": reason
              ,"body": body_field
              } 

        msgstring = self.mogrify(self.get_name(reason), msg)
        
        print(f"Sending event {msgstring}")
        try:
            self.pub.send_string(msgstring)
        except Exception as e: 
            print(f"Publishing ZMQ message failed with exception {e}") 
            return False
        print(f"Sent {msgstring}")

        return True


    def _heartbeat_loop(self):
        while self.running:
            #self.send_event(src=orover.origin.heartbeat
            #               ,reason=orover.event.heartbeat
            #               ,body={"status": "alive"})
            time.sleep(2)


    def handle_message(self, msg):
        pass


    def run(self):
        while self.running:
            msg = self.sub.recv_json()
            self.handle_message(msg)