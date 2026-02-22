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
     # event bus uses alternative method to create pub socket, using XSUB/XPUB sockets and zmq.proxy to allow for dynamic subscribers and publishers without needing to restart the event bus      

     def create_pub_socket(self, ctx):
          xpub = ctx.socket(zmq.XPUB)
          #xpub.bind("tcp://*:5555")
          xpub.bind(self.config.get("eventbus","bus_xpub_socket",fallback="tcp://*:5555"))
           
          return xpub

     def create_sub_socket(self, ctx):
          xsub = ctx.socket(zmq.XSUB)
          #xsub.connect("tcp://localhost:5556")
          xsub.connect(self.config.get("eventbus","bus_xsub_socket",fallback="tcp://localhost:5556"))
          return xsub


#### Main execution starts here ####

b = base() # Create an instance of the base class to get config and logger
zmq.proxy(b.sub, b.pub)