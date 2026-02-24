#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  zmq event bus for oRover processes to publish events to each other and the BOSS
"""
import zmq
import os
from base_process import baseprocess

class base(baseprocess):

     # No need to create a sub socket, we will use zmq.proxy to forward messages between the XSUB and XPUB sockets, so we don't need to create a sub socket here     
     def create_sub_socket(self, ctx):
          pass

# Signal handler for graceful shutdown of myself and child processes
     def terminate(self,signalNumber, frame):
          self.running = False
          os._exit(os.EX_OK) # sys.exit will not work here because of the socketserver, so we use os._exit to force exit immediately


#### Main execution starts here ####

b = base() # Create an instance of the base class to get config and logger

ctx = zmq.Context()
xsub = b.ctx.socket(zmq.XSUB)
xsub.connect(b.config.get("eventbus","bus_xsub_socket",fallback="tcp://localhost:5556"))
b.logger.debug(f"Event bus XSUB socket connected to {b.config.get('eventbus','bus_xsub_socket',fallback='tcp://localhost:5556')}")
xsub.bind("tcp://*:5556")


xpub = b.ctx.socket(zmq.XPUB)
xpub.bind(b.config.get("eventbus","bus_xpub_socket",fallback="tcp://*:5555"))
b.logger.debug(f"Event bus XPUB socket bound to {b.config.get('eventbus','bus_xpub_socket',fallback='tcp://*:5555')}")

zmq.proxy(xsub, xpub)
