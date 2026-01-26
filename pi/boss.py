#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: boss.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-25
Description:
    The BOSS
"""

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")