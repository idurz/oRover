#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
        License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
        Description  HCSR04 sensor client for the ROVER BOSS server
"""  

import time
from base_process import baseprocess
import RPi.GPIO as GPIO # pyright: ignore[reportMissingImports]
import oroverlib as orover
pinlist = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

class ultrasonic(baseprocess):
    def loop(self,sensors,object_notify_distance,polling_interval=0.5):
        while True:
            #Each sensor turn by turn
            for s in sensors:
                distance = measure_distance(s['echopin'],s['triggerpin'])
                if not distance is None and distance < object_notify_distance:
                    self.send_event(src = s['sensorid']
                                          ,reason = orover.event.object_detected
                                          ,body = {"distance": distance})
                        
                time.sleep(polling_interval)




# Get sensor info from config.ini. Sensors should be defined in section hcsr04 as sensor1, sensor2, etc. with value "name, triggerpin, echopin"
def getsensorinfo(p):
    sensors = []
    sensorcount = 0

    if not p.config.has_section('hcsr04'):
        p.logger.error("config.ini does not have a section [hcsr04] containing sensor information")
        return sensors

    while True:
        sensorcount = sensorcount + 1
        sensorstring = p.config.get("hcsr04",f"sensor{sensorcount}",fallback=None)
        if sensorstring is None:
            break 

        # Check if sensor parameters are in format name, triggerpin, echo pin
        sensorinfo = sensorstring.split(",")
        sensorinfo = [s.strip() for s in sensorinfo]
        if len(sensorinfo) != 3:
            p.logger.error(f"config.ini section hcsr04 for item sensor{sensorcount} should have 3 values, found {len(sensorinfo)} instead")
            break        
        p.logger.info(f"config.ini section hcsr04, found sensor{sensorcount} with values {sensorinfo}")

        # found 3 items. 1) Known sensor 2) Trigger pin 3) Echo pin
        sensorid = p.name_to_enum(sensorinfo[0])
        if sensorid is None:
            p.logger.error(f"config.ini section hcsr04, item sensor{sensorcount} is not defined as known sensor in origin")
            break  

        for i in range(1,3):
            if not sensorinfo[i].isnumeric():
                p.logger.error(f"config section [hcsr04], item sensor{sensorcount} pinnumbers should be numeric")
                break
            sensorinfo[i] = int(sensorinfo[i])
            if not(sensorinfo[i] in pinlist):
                p.logger.error  (f"config section [hcsr04], item sensor{sensorcount} pin is not within expected GPIO range 2..27 or already used by another sensor")
                break
            pinlist.remove(int(sensorinfo[i]))

        sensors.append({"sensorname" : sensorinfo[0]
                       ,"sensorid"   : sensorid
                       ,"triggerpin" : sensorinfo[1]
                       ,"echopin"    : sensorinfo[2]
                       })
        
        # Setup GPIO pins for this sensor
        GPIO.setup(sensorinfo[2],  GPIO.IN)  # echo pin
        GPIO.setup(sensorinfo[1],  GPIO.OUT) # trigger pin
        GPIO.output(sensorinfo[1], GPIO.LOW) # trigger pin

    return sensors




# Measure distance using HCSR04 sensor. Returns distance in cm or None if no echo received within timeout
def measure_distance(echo, trigger):

    GPIO.output(trigger, True) # Send trigger pulse
    time.sleep(0.00001)  # 10 µs
    GPIO.output(trigger, False)

    timeout = time.time() + 0.04  # Wait for echo start
    while GPIO.input(echo) == 0:
        if time.time() > timeout:
            return None
    start = time.time()

    timeout = time.time() + 0.04 # Wait for echo end
    while GPIO.input(echo) == 1:
        if time.time() > timeout:
           return None
        
    duration = time.time() - start
    distance_cm = (duration * 34300.0) / 2.0  # Speed of sound divided by path 2 to and from object
    return round(distance_cm, 1)




#### Main execution starts here ####
if __name__ == "__main__":
    
    p = ultrasonic()  # Initialize the process and connect to the event bus
    GPIO.setmode(GPIO.BCM) # use BCM pin numbering which is the same as the GPIO numbers

    sensors = getsensorinfo(p)
    min_obj_distance = float(p.config.get('hcsr04','min_obj_distance',fallback=20.0))
    polling_interval = float(p.config.get('hcsr04','polling_interval',fallback=0.5))

    p.loop(sensors, min_obj_distance, polling_interval) # Start the main loop to read sensors and send events