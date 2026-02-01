#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
   #     #   R     R   #      #   V     V   E         R     R
   #     #   R     R   #      #    V   V    E         R     R
   #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
   #     #   R   R     #      #     VV      E         R   R
    #####    R    R     ######      VV      EEEEEEE   R    R  
   Observation Remote Operated Vehicle Rover 

   File:        boss.py
   Copyright    (C) 2026 C v Kruijsdijk & P. Zengers
   License:     MIT License
   Created:     2026-01-27
   Description: The BOSS server for the ROVER. Cebtral point to receive 
                messages from clients and take appropriate actions to 
                actuators or respond to clients
"""

import zmq # pyright: ignore[reportMissingImports]
import orover_lib as osys
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def do_VisionEvent_objectDetected(socket, message):
    body = message.get('body', {})
    v = body.get('value', {})
    d = v.get('distance')

    if d is not None:
       print(f"BOSS: Warning: object too close from sensor {message.get('src')}: distance {d} cm")
       socket.send(b"OK")
    else:
       a = f"Received request: {message} without distance !!"
       socket.send(a.encode('utf-8'))


def do_system_shutdown(socket, message):
    reason = message.get('body', {}).get('value', 'unknown')
    print(f"BOSS: Shutdown requested, reason: {reason}")
    socket.send(b"Shutting down all systems")
    socket.close(linger=2500)
    context.term()
    exit(0)


while True:
    #  Wait for next request from client
    m = socket.recv()
    message = json.loads(m.decode('utf-8'))

    if "type" not in message:
         a = f"Received request: {message} without type !!"
         socket.send(a.encode('utf-8'))
         continue

    if message['type'] == osys.event.object_detected:
        do_VisionEvent_objectDetected(socket, message)
    elif message['type'] == osys.cmd.shutdown:
        do_system_shutdown(socket, message)
    else: 
        a = f"Received request: {message} with unsupported type {osys.tell_name(message['type'])} !!"
        socket.send(a.encode('utf-8'))
