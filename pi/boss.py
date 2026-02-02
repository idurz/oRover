#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
    #     #   R     R   #      #   V     V   E         R     R
    #     #   R     R   #      #    V   V    E         R     R
    #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
    #     #   R   R     #      #     VV      E         R   R
     #####    R    R     ######      VV      EEEEEEE   R    R  

   License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
   Description: The BOSS server for the ROVER. Cebtral point to receive messages
                from clients and take appropriate actions to actuators or 
                respond to clients"""

import zmq # pyright: ignore[reportMissingImports]
import orover_lib as orover
import json, sys, uuid
import logging
from pythonjsonlogger.json import JsonFormatter
from datetime import datetime

config = orover.readConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#logging.basicConfig(
#    format='%(asctime)s %(levelname)-8s %(message)s',
#    level=logging.INFO,
#    datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler(config.get('boss','logfile',fallback="orover.log"))
handler.setFormatter(JsonFormatter("{asctime} {message}", style="{"))
logger.addHandler(handler)


try:
    context = zmq.Context()
    context.setsockopt(zmq.SNDTIMEO,config.getint('boss','send_timeout',fallback=2500))

except Exception as e: 
    sys.exit(f"Could not create ZMQ context. Exception {e}" )

try:
    socket = context.socket(zmq.REP)
    socket.bind(config.get('boss','boss_socket',fallback='tcp://*:5555'))
except Exception as e: 
    sys.exit(f"Could not bind socket. Exception {e}" )


# ----------------------------------------

def handle_event_object_detected(message):
    sensor = orover.get_name(message.get('src'))
    body = message.get('body', {})
    if not "distance" in body:
        return f"message {message['id']} received without distance parameter in body"
    
    d = body.get('distance',0)
    print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
    return "OK"


def handle_cmd_shutdown(message):
    print(f"Shutdown message {message}")
    reason = message.get('body', {}).get('value', 'unknown')
    print(f"BOSS: Shutdown requested, reason: {reason}")
    socket.send(b"Shutting down all systems")
    socket.close(linger=2500)
    context.term()
    logger.info('Finished')
    exit(0)

# ----------------------------------------

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


def read_requests():
    #  Wait for next request from client
    m = socket.recv()

    # Check if valid json else discard
    try:
        message = json.loads(m.decode('utf-8'))
    except ValueError as e:
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

    DISPATCH = {orover.event.object_detected:            handle_event_object_detected
               ,orover.cmd.shutdown:                     handle_cmd_shutdown
               }

    try:
        handler = DISPATCH[message['reason']]
    except KeyError:
        return f"Discarding message {message['id']}: >>{message['reason']}<< is not a valid message reason!"
       
    result = handler(message)
    logger.info("Request handled", extra = {"request" : message, "result" : result})
    return result


def main():
    global logger, config, context, socket
  
    logger.info('Started')
   
    while True:
       answer = read_requests()
       socket.send(answer.encode('utf-8'))

if __name__ == "__main__":
    main()