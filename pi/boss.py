#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  The BOSS server for the ROVER. Handles messages related to 
                  object recognition and versatile exploration.
"""

import oroverlib as orover
from base_process import baseprocess, handler

class handler:
    """ Contains the handlers for BOSS messages. Each handler takes a message as input and returns a result string. 
        The handlers are called by the BOSS server when a message with the corresponding reason is received.
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
    def event_heartbeat(self, msg):
    
        global heartbeats
        # event.heartbeat {"id": "2d2dbb81-64f8-46bd-9585-2b64280af9a2", "ts": "2026-03-14T19:55:52.527138", "src": 1000, 
        # "me": "eventbus", "host": "robot", "prio": 5, "reason": 6402, "body": {"script": "eventbus"}}

        if "me" in msg and "ts" in msg:
           # store name and timestamp of last heartbeat for each script
           heartbeats[msg["me"]] = msg["ts"]
           p.logger.debug(f"Stored heartbeat from {msg['me']} at {msg['ts']}")
        return True
    
    def event_object_detected(self,message):
        sensor = p.enum_to_name(message.get('src'))
        body = message.get('body', {})
        if not "distance" in body:
            p.logger.warning(f"Message {message['id']} discarded from sensor {sensor}: received without distance parameter in body")
            return False
       
        d = body.get('distance',0)
        # dummy action: print warning if object too close
        print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
        return True
    
    def cmd_shutdown(self,socket,message,context, logger):
        print(f"Shutdown message {message}")
        reason = message.get('body', {}).get('value', 'unknown')
        print(f"BOSS: Shutdown requested, reason: {reason}")
        socket.send(b"OK")
        socket.close(linger=2500)
        context.term()
        logger.info('Finished')
        exit(0)


    
    

class base(baseprocess):
    pass

#### Main execution starts here ####
if __name__ == "__main__":
    
    heartbeats = {} # Dictionary to store the last heartbeat timestamp for each script, key is script name, value is timestamp of last heartbeat
    
    h = handler() # Instantiate the handler class, which contains the message handlers for the BOSS server
    p = base(handler=h) # Instantiate the base class, which contains the main loop and message handling logic for the BOSS server
    p.run() # Start the main loop of the BOSS server, which will listen for messages and call the appropriate handlers based on the message reason