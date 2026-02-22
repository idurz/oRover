#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Power control client for the ROVER BOSS server. Monitors a GPIO pin for power loss 
                  and initiates shutdown if power is lost.
"""

import os
import sys
import RPi.GPIO as GPIO
import time
from base_process import baseprocess

class base(baseprocess):

    def terminate(self,signalNumber, frame):
        self.pub.close()
        self.sub.close()
        self.ctx.term()
        self.running = False
        GPIO.cleanup()
        sys.exit()

    # Main loop 
    def run(self):
        while self.running:
            if GPIO.input(pin_number) == 0: #0==Low, if it detects cable is pulled
                time.sleep(sleep_time)
                if GPIO.input(pin_number) == 0: 
                    self.logger.critical("Power loss detected, initiating shutdown...")
                    os.system("sudo shutdown -h --no-wall now") 
            time.sleep(1)


#### Main execution starts here ####

b =base() # Create an instance of the base class to get config and logger

pin_number = b.config.getint("powercontrol","pin",fallback=4) #GPIO pin number to monitor, default is GPIO 4
sleep_time = b.config.getfloat("powercontrol","sleep_time",fallback=  2.0) #Seconds to wait before shutdown after detecting power loss

GPIO.setmode(GPIO.BCM) #Uses BCM pin numbering
GPIO.setup(pin_number, GPIO.IN)

b.run()