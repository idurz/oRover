#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  zmq event bus for oRover processes to publish events to each other and the BOSS
"""
import zmq
import os
import json
import threading
from base_process import baseprocess

class base(baseprocess):
     # event bus uses alternative method to create pub socket, using XSUB/XPUB sockets and zmq.proxy to allow for dynamic subscribers and publishers without needing to restart the event bus      
     def create_sub_socket(self, ctx):
          pass

     # Signal handler for graceful shutdown of myself and child processes
     def terminate(self,signalNumber, frame):
          self.running = False
          self.ctx.term()
          os._exit(os.EX_OK) # sys.exit will not work here because of the socketserver, so we use os._exit to force exit immediately


def log_proxy_message_ids():
     while b.running:
          try:
               frames = capture_rx.recv_multipart()
          except Exception as e:
               b.logger.error(f"Event bus capture receive failed: {e}")
               continue

          if not frames:
               continue

          # For multipart messages, the payload is in the last frame.
          payload = frames[-1].decode("utf-8", errors="replace")
          if " " not in payload:
               continue

          topic, msgtxt = payload.split(" ", 1)
          try:
               msg = json.loads(msgtxt)
          except json.JSONDecodeError:
               continue

          msg_id = msg.get("id")
          if msg_id is not None:
               b.logger.debug(f"Event bus proxied message id={msg_id} topic={topic}")

#### Main execution starts here ####

b = base() # Create an instance of the base class to get config and logger
#zmq.proxy(b.sub, b.pub)

xsub = b.ctx.socket(zmq.XSUB)
xsub.connect(b.config.get("eventbus","bus_xsub_socket",fallback="tcp://localhost:5556"))
b.logger.debug(f"Event bus XSUB socket connected to {b.config.get('eventbus','bus_xsub_socket',fallback='tcp://localhost:5556')}")
xsub.bind("tcp://*:5556")

xpub = b.ctx.socket(zmq.XPUB)
xpub.bind(b.config.get("eventbus","bus_xpub_socket",fallback="tcp://*:5555"))
b.logger.debug(f"Event bus XPUB socket bound to {b.config.get('eventbus','bus_xpub_socket',fallback='tcp://*:5555')}")

if b.config.getboolean("eventbus","capture_message_ids",fallback=False):
     b.logger.info("Event bus message ID capture enabled")

     capture_endpoint = "inproc://eventbus-capture"
     capture_tx = b.ctx.socket(zmq.PAIR)
     capture_tx.bind(capture_endpoint)

     capture_rx = b.ctx.socket(zmq.PAIR)
     capture_rx.connect(capture_endpoint)

     threading.Thread(target=log_proxy_message_ids, daemon=True).start()

     zmq.proxy(xsub, xpub, capture_tx)

else:
     b.logger.info("Event bus message ID capture disabled")
     zmq.proxy(xsub, xpub)