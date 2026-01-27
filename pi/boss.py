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

import time
import zmq
import orover_lib
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    m = socket.recv()
    message = json.loads(m.decode('utf-8'))

    if "value" in message:
       v = message['value'].get('distance')
       d = v['distance']
       u = v['unit']

       print(f"BOSS: Warning: object to close from sensor {message['source']}: distance {d} {u}")
       socket.send(b"OK")
    else:
       a = f"Received request: {message} without distance !!"
       socket.send(a.encode('utf-8'))
