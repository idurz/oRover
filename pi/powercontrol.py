#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Power control client for the ROVER BOSS server. Monitors a GPIO pin for power loss 
                  and initiates shutdown if power is lost.
"""

import os
import sys
import RPI.GPIO as GPIO
import time
import signal
import logging, logging.handlers
import oroverlib as orover
import setproctitle

# Signal handler for graceful shutdown of myself and child processes
def terminate(signalNumber, frame):
    GPIO.cleanup()
    sys.exit()


#### Main execution starts here ####

config = orover.readConfig()
logger = orover.setlogger(config)
setproctitle.setproctitle(f"orover:{orover.getmodulename(config)}")

pin_number = config.getint("powercontrol","pin",fallback=4) #GPIO pin number to monitor, default is GPIO 4
sleep_time = config.getfloat("powercontrol","sleep_time",fallback=  2.0) #Seconds to wait before shutdown after detecting power loss

GPIO.setmode(GPIO.BCM) #Uses BCM pin numbering
GPIO.setup(pin_number, GPIO.IN)

# Start done, register signal handler for graceful shutdown
signal.signal(signal.SIGTERM, terminate)

while True:
    if GPIO.input(pin_number) == 0: #0==Low, if it detects cable is pulled
        time.sleep(sleep_time)
        if GPIO.input(pin_number) == 0: 
            os.system("sudo shutdown -h now") 
    time.sleep(1)