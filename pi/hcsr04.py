#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
    #     #   R     R   #      #   V     V   E         R     R
    #     #   R     R   #      #    V   V    E         R     R
    #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
    #     #   R   R     #      #     VV      E         R   R
     #####    R    R     ######      VV      EEEEEEE   R    R  

   License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
   Description: HCSR04 sensor client for the ROVER BOSS server
"""

import zmq # pyright: ignore[reportMissingImports]
import orover_lib as orover
import time
import RPi.GPIO as GPIO # pyright: ignore[reportMissingImports]
import json, uuid, os
from datetime import datetime



# read [hcsr04] from config with configparser



# open zmg
#socket = orover.connect_to_server()

# TRIGGER_PIN = 17  # Pin of the first trigger
# ECHO_PIN    = 27  # Pin of the common echo (must be an interrupt pin)

# def measure_distance():
#     # Send trigger pulse
#     start = time.time()
#     end = time.time()

#     GPIO.output(TRIGGER_PIN, True)
#     time.sleep(0.00001)  # 10 µs
#     GPIO.output(TRIGGER_PIN, False)

#     # Wait for echo start
#     timeout = time.time() + 0.04
#     while GPIO.input(ECHO_PIN) == 0:
#         if time.time() > timeout:
#             return None
#         start = time.time()

#     # Wait for echo end
#     timeout = time.time() + 0.04
#     while GPIO.input(ECHO_PIN) == 1:
#         if time.time() > timeout:
#             return None
#         end = time.time()

#     duration = end - start

#     # Speed of sound: 34300 cm/s
#     distance_cm = (duration * 34300) / 2
#     return round(distance_cm, 1)

def main():

    print("HC-SR04 client. Press Ctrl-C to exit")
    config = orover.readConfig()
    if not config.has_section('hcsr04'):
          print("config.ini does not have a section for this sensor")
          return

    sensorcount = 0
    while True:
        sensorcount = sensorcount + 1
        ff = config.get("hcsr04",f"sensor{sensorcount}",fallback=None)
        if not ff is None:
            print(f"Found sensor {sensorcount} with values {ff}")
        else:
            sensorcount = sensorcount - 1
            break 
    print(f"Total {sensorcount} sensors")

#     # GPIO setup
#     GPIO.setmode(GPIO.BCM) # use BCM pin numbering which is the same as the GPIO numbers
#     GPIO.setup(ECHO_PIN,GPIO.IN) 
#     GPIO.setup(TRIGGER_PIN,GPIO.OUT) 
#     GPIO.output(TRIGGER_PIN, GPIO.LOW)

#     try:
#         while True:
#             distance = measure_distance()
#             if not distance is None and distance < 20:
#                 msg = {"id": str(uuid.uuid4())
#                        ,"ts": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
#                        ,"src": orover.origin.sensor_ultrasonic_front
#                        ,"me": os.path.basename(__file__)
#                        ,"prio": orover.priority.low
#                        ,"type": orover.event.object_detected
#                        ,"body": {"value": {"distance": distance}}
#                        }
#                 print(f"HCSR04: Sending message {msg}")

#                 socket.send(json.dumps(msg).encode('utf-8'))
#                 answer = socket.recv()
#                 print(f"HCSR04: Boss told me {answer}")

#             time.sleep(0.5)
#     except KeyboardInterrupt:
#         print("\nStopping...")
#     finally:
#         GPIO.cleanup()

if __name__ == "__main__":
    main()
