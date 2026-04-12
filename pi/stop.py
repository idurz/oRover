#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Web server for oRover, for manual control and monitoring
"""
import oroverlib as orover
from base_process import baseprocess, handler

class base(baseprocess):
    pass

p = base()

msg = "Requesting oRover to stop by stop.py"
print(msg)
p.logger.info(msg)

p.send_event(src = orover.origin.orover_stopper
            ,reason = orover.cmd.shutdown
            ,body = {"value": "requested by stop.py"}
            )
