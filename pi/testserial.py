#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  interface for UGV control (motor commands etc)
"""


import serial

serial_dev = "/dev/serial0"
serial_baud = 115200
print(f"Opening serial port {serial_dev} with baudrate {serial_baud}")

serial_port = serial.Serial(serial_dev, 115200, timeout=1)
s = f'{{"T":1,"L":0.5,"R":0.5}}\n'
print
serial_port.write(s.encode())
a = serial_port.readline()
print(a.decode(errors="ignore"))
serial_port.close()
