#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
File: boss.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-27
Description:
    The BOSS
"""


import zmq
import orover_lib as osys
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def do_VisionEvent_objectDetected(socket, message):
    if "values" in message:
       v = message['values'].get('distance')
       d = v

       print(f"BOSS: Warning: object to close from sensor {message['src']}: distance {d} cm")
       socket.send(b"OK")
    else:
       a = f"Received request: {message} without distance !!"
       socket.send(a.encode('utf-8'))

def do_system_shutdown(socket, message):
    reason = message['body'].get('reason','unknown')
    print(f"BOSS: Shutdown requested, reason: {reason}")
    socket.send(b"Shutting down all systems")
    socket.close()
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

    if message['type'] == osys.tell.VisionEvent.objectDetected:
        do_VisionEvent.objectDetected(socket, message)
    elif message['type'] == osys.tell.system.shutdown:
        do_system.shutdown(socket, message)
    else: 
        a = f"Received request: {message} with unsupported type {osys.tell.getname(message['type'])} !!"
        socket.send(a.encode('utf-8'))
