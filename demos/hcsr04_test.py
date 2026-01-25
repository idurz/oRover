#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: hcsr04_test.py
Copyright (C) 2022 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-25
Description:
    Testing with the HC-SR04 ultrasonic distance sensor
"""

import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import threading

# ---------------- CONFIG ----------------

ECHO_PIN = 2  # Pin of the common echo (must be an interrupt pin)
TRIGGER_PIN = 4  # Pin of the first trigger

PINGDELAY = 100 # ms Time between each new measurement
SOUNDSPEED = 343.0 # Speed of sound in m/s
TIMEOUT = 0.03  # 30 ms timeout for echo

# ------ runtime/shared variables -------

startEcho = 0
stopEcho = 0
_echo_lock = threading.Lock()

def micros():
    # high resolution microseconds timestamp
    return time.perf_counter_ns() // 1000

def ISR_ECHO(channel):
    global startEcho, stopEcho
    # keep ISR short
    now = micros()
    if GPIO.input(ECHO_PIN):
        with _echo_lock:
            startEcho = now
    else:
        with _echo_lock:
            stopEcho = now


def doMeasurement():
    global startEcho, stopEcho
    timeout_s = TIMEOUT
    with _echo_lock:
        startEcho = 0
        stopEcho = 0

    # Trigger pulse: HIGH for >=10µs
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(10e-6)
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    start_wait = time.time()
    while True:
        with _echo_lock:
            se = startEcho
            sp = stopEcho

        if se != 0 and sp != 0:
            # got both edges
            elapsed_s = (sp - se) / 1_000_000.0
            return elapsed_s * SOUNDSPEED * 100.0 / 2.0
        
        if time.time() - start_wait >= timeout_s:
            return "timeout" 

  
def main():

    # GPIO setup
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM) # use BCM pin numbering which is the same as the GPIO numbers
    GPIO.setup(ECHO_PIN,GPIO.IN) 
    GPIO.setup(TRIGGER_PIN,GPIO.OUT) 
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    GPIO.add_event_detect(ECHO_PIN, GPIO.BOTH, callback=ISR_ECHO, bouncetime=1)

    distancesCm = 0.0
    last_ping = 0.0
    while True:
        if (time.time() - last_ping) * 1000.0 >= PINGDELAY:

            distancesCm = doMeasurement()
            print(f"Distance {distancesCm} cm")
   
            last_ping = 0.0
            time.time()
            time.sleep(1) # small delay to avoid busy loop


if __name__ == "__main__":
    main()
