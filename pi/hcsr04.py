#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
        License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
        Description  HCSR04 sensor client for the ROVER BOSS server
"""  

import time
from base_process import BaseProcess
import RPi.GPIO as GPIO # pyright: ignore[reportMissingImports]
import orover_lib as orover

class Ultrasonic(BaseProcess):
    def loop(self,sensors,object_notify_distance):
        while True:
            #Each sensor turn by turn
            for s in sensors:
                distance = measure_distance(s['echopin'],s['triggerpin'])
                if not distance is None and distance < object_notify_distance:
                    print(f"Object detected by sensor {s['sensorid']} at distance {distance} cm")
                    if not self.send_event(src = s['sensorid']
                                            ,reason = orover.event.object_detected
                                            ,body = {"distance": distance}):
                        print(f"hcssr04 Failed to send event for sensor {s['sensorid']}")   
                time.sleep(0.5)


def getsensorinfo(config):
    sensors = []

    if not config.has_section('hcsr04'):
        print("config.ini does not have a section for this sensor")
        return False

    sensorcount = 0
    while True:
        sensorcount = sensorcount + 1
        sensorstring = config.get("hcsr04",f"sensor{sensorcount}",fallback=None)
        if sensorstring is None:
            break 

        # Check if sensor parameters are in format name, triggerpin, echo pin
        sensorinfo = sensorstring.split(",")
        sensorinfo = [s.strip() for s in sensorinfo]
        if len(sensorinfo) != 3:
            print(f"config.ini section hcsr04 for item sensor{sensorcount} should have 3 values, found {len(sensorinfo)} instead")
            break        

        # found 3 items. 1) Known sensor 2) Trigger pin 3) Echo pin
        if not sensorinfo[0] in orover.origin._member_names_:
            print(f"config.ini section hcsr04, item sensor{sensorcount} is not a valid sensor id in origin")
            break
        sensorid = orover.origin.find_by_name(sensorinfo[0])
        
        if not(sensorinfo[1].isnumeric() and int(sensorinfo[1]) > 1 and int(sensorinfo[1]) < 28):
            print(f"config.ini section hcsr04, item sensor{sensorcount} trigger pin is not within expected GPIO range 2..27")
            break

        if not(sensorinfo[2].isnumeric() and int(sensorinfo[2]) > 1 and int(sensorinfo[2]) < 28):
            print(f"config.ini section hcsr04, item sensor{sensorcount} echo pin is not within expected GPIO range 2..27")
            break

        sensors.append({"sensorname" : sensorinfo[0]
                       ,"sensorid"   : sensorid
                       ,"triggerpin" : int(sensorinfo[1])
                       ,"echopin"    : int(sensorinfo[2])
                       })
        
    return sensors

def measure_distance(echo, trigger):
    GPIO.output(trigger, True)
    time.sleep(0.00001)  # 10 µs
    GPIO.output(trigger, False)

    # Wait for echo start
    timeout = time.time() + 0.04 
    while GPIO.input(echo) == 0:
        if time.time() > timeout:
            return None
        #time.sleep(0.001)  # sleep 1 ms
    start = time.time()

    # Wait for echo end
    timeout = time.time() + 0.04
    while GPIO.input(echo) == 1:
        if time.time() > timeout:
           return None
        #time.sleep(0.001)  # sleep 1 ms
    duration = time.time() - start
    distance_cm = (duration * 34300.0) / 2.0  # Speed of sound: 34300 cm/s divided by 2 (to and from object)
    return round(distance_cm, 1)


if __name__ == "__main__":
    p = Ultrasonic()
    sensors = getsensorinfo(p.config)
    object_notify_distance = float(p.config.get('hcsr04','object_notify_distance',fallback=20.0))

    # GPIO setup
    GPIO.setmode(GPIO.BCM) # use BCM pin numbering which is the same as the GPIO numbers

    for s in sensors:
        print(f"Setting up {s['sensorname']}")
        GPIO.setup(s['echopin'],     GPIO.IN)  # echo pin
        GPIO.setup(s['triggerpin'],  GPIO.OUT) # trigger pin
        GPIO.output(s['triggerpin'], GPIO.LOW) # trigger pin

    p.loop(sensors, object_notify_distance )