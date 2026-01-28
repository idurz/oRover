#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: stop.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-27
Description:
    Request boss to stop and close all connections
"""
import zmq
import orover_lib as osys

print("Requesting BOSS to stop")
config = osys.readConfig()

# open zmg
context = zmq.Context()
print("Connecting to BOSS")
socket = context.socket(zmq.REQ)
socket.connect(config['boss']['socket'])

def main():
    answer = osys.tell.toboss(socket, 
                                    {"src":  osys.origin.controller.remote_interface
                                    ,"prio": osys.priority.low
                                    ,"type": osys.tell.system.shutdown
                                    ,"body": {"reason":"maintenance"}
                                    })
    print(f"HCSR04: Boss told me {answer}")

if __name__ == "__main__":
    main()
