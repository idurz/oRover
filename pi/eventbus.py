#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  zmq event bus for oRover processes to publish events to each other and the BOSS
"""
import sys
import zmq
import oroverlib as orover
import setproctitle
import os

#### Main execution starts here ####

config = orover.readConfig()
logger = orover.setlogger(config)
setproctitle.setproctitle(f"orover:{orover.getmodulename(config)}")

ctx = zmq.Context()
xsub = ctx.socket(zmq.XSUB)
xsub.bind("tcp://*:5556")

xpub = ctx.socket(zmq.XPUB)
xpub.bind("tcp://*:5555")

logger.info(f"{orover.getmodulename(config)} started with PID {os.getpid()}")
#print("  publishers -> tcp://*:5556")
#print("  subscribers -> tcp://*:5555")

zmq.proxy(xsub, xpub)