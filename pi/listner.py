#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Simple listener process for receiving messages from the event bus, just for debug purposes
"""
import json
import zmq
import oroverlib as orover

def demogrify(topicmsg):
     # Find first occurrence of '{' to separate topic and message, then JSON decode the message part
     try:
          topic, msgtxt = topicmsg.split(' ', 1)
     except ValueError:
          print(f"Received malformed message: >>{topicmsg}<<, unable to split topic and message")
          return None, None
        
     return topic, json.loads(msgtxt)


def _parse_csv(value):
     # Parse comma-separated values into a cleaned list.
     if not value:
          return []
     return [item.strip() for item in value.split(",") if item.strip()]


def load_listener_settings():
     config, config_file = orover.readConfig(True)

     # Keep backward compatibility: [lister] was used previously in config.ini.
     section = "listner" if config.has_section("listner") else "lister"

     endpoint = config.get(
          section,
          "sub_socket",
          fallback=config.get("eventbus", "client_sub_socket", fallback="tcp://localhost:5555"),
     )
     subscribe_filter = config.get(section, "subscribe", fallback="")

     ignore_topics = _parse_csv(config.get(section, "ignore_topics", fallback=""))
     if config.getboolean(section, "ignore_heartbeat", fallback=True):
          ignore_topics.append("event.heartbeat")

     # Deduplicate while preserving order.
     ignore_topics = list(dict.fromkeys(ignore_topics))

     print(f"Listener using config file {config_file}, section [{section}], endpoint {endpoint}")
     return endpoint, subscribe_filter, ignore_topics

ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
endpoint, subscribe_filter, ignore_topics = load_listener_settings()
sock.connect(endpoint)
sock.setsockopt_string(zmq.SUBSCRIBE, subscribe_filter)

while True:
    msg = sock.recv_string()
    
    topic, msgdict = demogrify(msg)
    if topic not in ignore_topics:
        print(f"{msgdict}")