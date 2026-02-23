#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  simple test process to validate the logging receiver is working
"""
import logging, logging.handlers
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
socketHandler = logging.handlers.SocketHandler('localhost',
                     logging.handlers.DEFAULT_TCP_LOGGING_PORT)
rootLogger.addHandler(socketHandler)
log = logging.getLogger("logtester")


log.setLevel("DEBUG")

print("This is a test of the logging system, sending DEBUG, INFO, WARNING, ERROR, and CRITICAL messages to the logging receiver")    
log.debug("This is a debug message from logtester")
log.info("This is an info message from logtester")
log.warning("This is a warning message from logtester")
log.error("This is an error message from logtester")
log.critical("This is a critical message from logtester")
print("Done sending log messages")
