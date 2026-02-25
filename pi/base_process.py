#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  base process class for all rover processes, providing common functionality like event handling and heartbeat
"""

import datetime
import socket
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

class handler:
    pass


class baseprocess:
    # Base class for all processes, providing common functionality like event handling and heartbeat

    def __init__(self):
        # Beam me up, Scotty! Initialize the process, read configuration, set up logging and ZMQ sockets, and prepare for message handling and heartbeat

        self.config, self.configfile = orover.readConfig(True)  # Read configuration from config.ini file
        self.myname = self.getmodulename(self.config)  # Get the name of the current script for use in messages
        self.get_lock() # Get a lock to prevent multiple instances of the same script running at the same time

        self.logger = self.setlogger(self.config, self.myname)
        setproctitle.setproctitle(f"orover:{self.myname}")

        #self.handler  = handler()
        #print(f"Starting server with handlers: {dir(self.handler)}")
        
        #self.handler = handler() # Create an instance of the handler class to load the message handlers defined in the class
        
        self.ctx = zmq.Context() # Create ZMQ context
        self.pub = self.create_pub_socket(self.ctx) # Create zmq PUB socket for event bus, connect to port
        self.sub = self.create_sub_socket(self.ctx) # Create zmq SUB socket for event bus, bind to port

        self.dispatch = {}
        self.known_topics = []
        
        # Start done, register signal handler for graceful shutdown and log the start of the process
        signal.signal(signal.SIGTERM, self.terminate)
        self.running = True

        if self.logger is not None:
            self.logger.info(f"{self.myname} started with PID {os.getpid()}")
        print(f"{self.myname} started with PID {os.getpid()}")

        # is heart_beat_interval configured? If so, start the heartbeat thread
        self.heart_beart_interval = self.config.getint('orover','heartbeat_interval',fallback=0)
        if self.heart_beart_interval > 0:
            self.hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.hb_thread.start()


    def get_lock(self):
        # Without holding a reference to our socket somewhere it gets garbage collected when the function exits
        #socket.get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        ##try:
        #    # The null byte (\0) means the socket is created in the abstract namespace instead of being created 
        #    # on the file system itself. Works only in Linux
        #    socket.get_lock._lock_socket.bind('\0' + self.myname)
        #except socket.error:
        #    print(f"Lock exists already for script {self.myname}, please stop previous instance before starting a new one")
        #    sys.exit()
        return
   
    
    def getmodulename(self, config):
        # Returns the name of the current module, based on the filename of the script, or the name defined in the config file if it matches the current 
        # script name. This allows for more flexible naming of processes in the config file
        if sys.argv[0] in config.items('scripts'): # sys.argv[0] contains the name of the currently running script, no path and with ".py" extension.
            print(f"Found script name {sys.argv[0]} in config, using corresponding name {config.get('scripts',sys.argv[0])} for logging")
            for name, path in config.items('scripts'): # find item in config that matches the current script name and return the key (name) of that item
                if sys.argv[0] == os.path.basename(path):
                    return name
            return "default"  # default name if not found in config
        return sys.argv[0].split('.')[0]


    def log_timestamp(self):
        # Return the current timestamp in a format suitable for logging, e.g. "20240610123045" for June 10, 2024 at 12:30:45
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    
    def setlogger(self,config,myname):
        # Set up logging to send log messages to the boss process via a socket handler
        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.DEBUG)
        socketHandler = logging.handlers.SocketHandler('localhost',
                     logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        rootLogger.addHandler(socketHandler)
        logger = logging.getLogger(myname)

        loglevel = config.get('orover','loglevel',fallback="UNKNOWN").upper()
        known_level = (loglevel in ["DEBUG","INFO","WARNING","ERROR","CRITICAL"])
        if not known_level:
            logger.setLevel("ERROR")
            logger.error((f"Invalid log level {loglevel} in config, defaulting to 'ERROR'"))
        else:
            logger.setLevel(loglevel.upper())
    
        return logger
 

    def create_pub_socket(self, ctx):
        # Create a ZMQ PUB socket and connect to the event bus for publishing messages
        pub = ctx.socket(zmq.PUB)
        pub.connect(self.config.get("eventbus","client_pub_socket",fallback="tcp://localhost:5556"))
        if self.logger is not None:
            self.logger.debug(f"Created PUB socket and connected to {self.config.get('eventbus','client_pub_socket',fallback='tcp://localhost:5556')}")
        return pub

    def create_sub_socket(self, ctx):
        # Create a ZMQ SUB socket and connect to the event bus for receiving messages, subscribe to all topics
        sub = ctx.socket(zmq.SUB)
        sub.connect(self.config.get("eventbus","client_sub_socket",fallback="tcp://localhost:5555"))
        sub.setsockopt_string(zmq.SUBSCRIBE, "")
        if self.logger is not None:
            self.logger.debug(f"Created SUB socket and connected to {self.config.get('eventbus','client_sub_socket',fallback='tcp://localhost:5555')}")
        return sub
        
    
    def enum_to_name(self, val) -> str:
        # Return the best-effort name for a numeric type.
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
            try:
                return f"{cls(val).__class__.__name__}.{cls(val).name}"
            except ValueError:
                pass
        return f"{cls(val).__class__.__name__}.unknown({val})"

    
    def name_to_enum(self, name):
        # Return the best-effort number based on a name 
        for cls in (orover.priority, orover.operational_mode, orover.lifecycle_stage, orover.power_source,
                    orover.health_status, orover.origin,orover.actuator, orover.controller, orover.cmd,
                    orover.state, orover.event):
            try:
                return cls[name]
            except KeyError:
                pass
        return None

    
    def terminate(self,signalNumber, frame):
        # Signal handler for graceful shutdown of myself and child processes
        self.pub.close()
        self.sub.close()
        self.ctx.term()
        self.running = False
        sys.exit()

    
    def mogrify(self, topic, msg):
        # json encode the message and prepend the topic
        return topic + ' ' + json.dumps(msg)


    def demogrify(self, topicmsg):
        # Return the topic and JSON decoded message from the topic+message string received from the bus
        # Find first occurrence of '{' to separate topic and message, then JSON decode the message part
        try:
            topic, msgtxt = topicmsg.split(' ', 1)
        except:
            self.logger.error(f"Received malformed message: >>{topicmsg}<<, unable to split topic and message")
            return None, None
        return topic, json.loads(msgtxt)
    

    def send_event(self, src, reason,body={}, prio=None):
        # Publish an event to the bus, with validation of fields and JSON body
        if self.logger is not None:
            self.logger.debug(f"Preparing to send event with src {src}, reason {reason}, body {body} and prio {prio}")

        if not isinstance (src,(orover.origin, orover.actuator, orover.controller)):
            if self.logger is not None:
                self.logger.error(f"Invalid 'src' field, must be known enum ({src})")
            return False
    
        if not isinstance(reason, (orover.cmd, orover.state, orover.event)):
            if self.logger is not None:
                self.logger.error(f"Invalid 'reason' field must be known enum ({reason})")
            return False

        # check if body is valid json
        body_field = body
        if isinstance(body, str):
            try:
                body_field = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                if self.logger is not None:
                    self.logger.error(f"{body} is not valid JSON")
                return False

        # priority: accept an int or Priority member
        if prio is None:
            prio = orover.priority.normal
            if not isinstance(prio,orover.priority):
                if self.logger is not None:
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
        msgstring = self.mogrify(self.enum_to_name(reason), msg)
        if self.logger is not None:
            self.logger.debug(f"Sending event {json.dumps(msg)}")

        try:
            self.pub.send_string(msgstring)
        except Exception as e: 
            if self.logger is not None:
                self.logger.error(f"Publishing ZMQ message failed with exception {e}") 
            return False

        return True

    
    def _heartbeat_loop(self):
        # Heartbeat loop, sending a heartbeat event at the configured interval
        while self.running:
            self.send_event(src=orover.origin.heartbeat
                           ,reason=orover.event.heartbeat
                           ,body={"script": self.myname})
            time.sleep(self.heart_beart_interval)

    
    def all_fields_present(self, message):
        # test method to validate if all fields are present in the message
        """ "id"    : UUID
           ,"ts"    : datetime of message in '%Y-%m-%dT%H:%M:%S.%f' format
           ,"src"   : message source, e.g. specific sensor or actuator, should be in class origin
           ,"me"    : sending script name
           ,"host"  : sending node
           ,"prio"  : priority of message, should be in class priority
           ,"reason": type of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"body"  : contains parameters depending on type of message
        """
        if message is None:
            return False
        
        # print(f"Validating message {message} for required fields")
        for s in ["id","ts","src","me","host","prio","reason","body"]:
            afp = (s in message)
            if not afp:
                break
            return afp

    
    def valid_uuid(self, id):
        # test method to validate uuid
        try:
            uuid_object = uuid.UUID(id, version=4).hex
        except ValueError:
            return False
        return True


    def valid_datetime(self, ts):
        # test method to validate datetime
        try:
            date_object = datetime.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            return False
        return True

    
    def valid_source(self, src):
        # test method to validate source
        return src in orover.controller, orover.origin
   
    
    def valid_priority(self,prio):
        # test method to validate priority
        return prio in orover.priority

    
    def valid_message(self, msg):
        # Check if the message has the required fields and valid values, return True if valid, False otherwise
        if not self.all_fields_present(msg):
            if self.logger is not None:
                self.logger.error(f"Discarding message {msg} --> Field missing in message")
            return False
        if not self.valid_uuid(msg['id']):
            if self.logger is not None:
                self.logger.error(f"Discarding message {msg} --> {msg['id']}<< is not a valid UUID version 4")
            return False
        if not self.valid_datetime(msg['ts']):
            if self.logger is not None:
                self.logger.error(f"Discarding message {msg['id']}: >>{msg['ts']}<< is not a valid datetime in format '%Y-%m-%dT%H:%M:%S.%f'")
            return False
        if not self.valid_source(msg['src']):
            if self.logger is not None:
                self.logger.error(f"Discarding message {msg['id']}: >>{msg['src']}<< is not a valid origin")
            return False
        if not self.valid_priority(msg['prio']):
            if self.logger is not None:
                self.logger.error(f"Discarding message {msg['id']}: >>{msg['prio']}<< is not a valid priority")
            return False
        if self.logger is not None:
            self.logger.debug(f"Validated message {msg}")
        return True


    def handle_message(self, topicmsg):
        # retrieve the topic and message from the received zmq message, and validate the message structure and content
        topic , msg = self.demogrify(topicmsg)
        if topic in self.known_topics:
            if self.valid_message(msg):
                reason = msg['reason']
                try:
                    handler_routine = self.dispatch[reason]
                except KeyError:
                    self.logger.error(f"Message discarded: {msg['id']}: No handler for reason {self.enum_to_name(reason)} available in {self.myname} server") 
                    return
                result = handler_routine(msg)
                self.logger.debug(f"Message handled : {msg}, result: {result}")
                return result
        return None   


    def run(self):
        # Main loop to receive messages from the bus and handle them, runs until termination signal is received
        for j in dir(self.handler):

            if callable(getattr(self.handler, j)) and not j.startswith("__"):
                c, topic = j.split("_", 1)
                self.logger.debug(f"Registering handler for topic {topic} as {self.name_to_enum(topic)}")
                self.dispatch[self.name_to_enum(topic)] = getattr(self.handler, j)
                self.known_topics.append(f"{c}.{topic}")

        while self.running:
            # read topic and message from the SUB socket, then handle the message
            topicmsg = self.sub.recv_string()
            result = self.handle_message(topicmsg)