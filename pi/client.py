#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: client.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-25
Description:
    Test client for the BOSS
"""
import zmq

context = zmq.Context()
print("Connecting to Server on port 5555")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print('Sending Hello')
socket.send(b"Hello")
print('Waiting for answer')
message = socket.recv()
print(f"Received: {message}")