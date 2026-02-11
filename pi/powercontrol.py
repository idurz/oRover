#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Power control client for the ROVER BOSS server. Monitors a GPIO pin for power loss 
                  and initiates shutdown if power is lost.
"""

import configparser
import argparse
import os
import sys
import RPI.GPIO as GPIO
import time
import signal


# Signal handler for graceful shutdown of myself and child processes
def terminate(signalNumber, frame):
    GPIO.cleanup()
    sys.exit()


#### Main execution starts here ####


# Check if config file is given as argument, otherwise use default
parser = argparse.ArgumentParser(description="oRover startup script"
                                ,prog="python3 launcher.py")
parser.add_argument("--config"
                   ,type=str
                   ,required=False
                   ,default="config.ini"
                   ,help="Path to configuration file (default: config.ini)")

args = parser.parse_args()
print(f"Using configuration file: {args.config}")

# Read configuration from config.ini file
config = None   
if not os.path.isfile(args.config):
    sys.exit(f"Configuration file {args.config} does not exist")

config = configparser.ConfigParser() 
config.read(args.config)

pin_number = config.get("powercontrol","pin",fallback=4) #GPIO pin number to monitor for power control, default is GPIO 4
sleep_time = config.getfloat("powercontrol","sleep_time",fallback=2.0) #Time to wait before shutdown after detecting power loss
GPIO.setmode(GPIO.BCM) #Uses BCM pin numbering (i.e., the GPIO number, not the pin number)
GPIO.setup(pin_number, GPIO.IN)

# Start done, register signal handler for graceful shutdown
signal.signal(signal.SIGTERM, terminate)

while True:
    if GPIO.input(pin_number) == 0: #0==Low, if it detects cable is pulled
        time.sleep(sleep_time)
        if GPIO.input(pin_number) == 0: 
            os.system("sudo shutdown -h now") 
    time.sleep(1)  