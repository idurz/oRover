#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: hcsr04_test.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-25
Description:
    Testing with the HC-SR04 ultrasonic distance sensor
"""

import time
import sys
import RPi.GPIO as GPIO

TRIGGER_PIN = 17  # Pin of the first trigger
ECHO_PIN    = 27  # Pin of the common echo (must be an interrupt pin)

#SENSORS = {
#    "LEFT":  {"trig": 17, "echo": 27},
#    "FRONT": {"trig": 22, "echo": 23},
#    "RIGHT": {"trig": 24, "echo": 25},
#}


def measure_distance():
    # Send trigger pulse
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)  # 10 µs
    GPIO.output(TRIGGER_PIN, False)

    # Wait for echo start
    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 0:
        if time.time() > timeout:
            return None
        start = time.time()

    # Wait for echo end
    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 1:
        if time.time() > timeout:
            return None
        end = time.time()

    duration = end - start

    # Speed of sound: 34300 cm/s
    distance_cm = (duration * 34300) / 2
    return round(distance_cm, 1)

def main():
    # GPIO setup
    GPIO.setmode(GPIO.BCM) # use BCM pin numbering which is the same as the GPIO numbers
    GPIO.setup(ECHO_PIN,GPIO.IN) 
    GPIO.setup(TRIGGER_PIN,GPIO.OUT) 
    GPIO.output(TRIGGER_PIN, GPIO.LOW)

    print("HC-SR04 test program. Press Ctrl-C to exit")
    try:
        while True:
            distance = measure_distance()
            if distance is None:
                print(f"Out of range")
            else:
                print(f"{distance} cm")
            print("-" * 30)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()