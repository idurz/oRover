#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Simple listener process for receiving messages from the event bus, just for debug purposes
"""
import json
import zmq

def demogrify(topicmsg):
     # Find first occurrence of '{' to separate topic and message, then JSON decode the message part
     try:
          topic, msgtxt = topicmsg.split(' ', 1)
     except:
          print(f"Received malformed message: >>{topicmsg}<<, unable to split topic and message")
          return None, None
        
     return topic, json.loads(msgtxt)

ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://localhost:5555")
sock.setsockopt_string(zmq.SUBSCRIBE, "")

ignore_topics = ["event.heartbeat"]
while True:
    msg = sock.recv_string()
    
    topic, msgdict = demogrify(msg)
    if topic not in ignore_topics:
        print(f"{msgdict}")