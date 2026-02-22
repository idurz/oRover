#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r -> object recognition and versatile exploration robot
     License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description: Allow testing of the BOSS server with command-line tool
"""

import json

import oroverlib as orover
from base_process import baseprocess

class base(baseprocess):
    pass

def printlist():
    print("")
    print("Available commands:")
    print("------------------")
    for cmd in orover.cmd: 
        print(f"\033[0;32m{cmd.name}\033[0m")


def main():
    print("Starting command line test tool...")
    print("\033[1;31mThis tool does not check the validity of the commands or parameters, so use with caution!\033[0m")
    b = base()
    
    while True:

        printlist()
        print("")
        command = input("\033[0;0mEnter command (or 'exit' to quit): ")

        if command.lower() == 'exit':
            print("Exiting command line test tool.")
            return

        params = []
        while True: 
            p = input("\033[0;0mEnter parameter (or just enter to quit): ")
            if not p:
                break

            v = input(f"\033[0;0mEnter value for parameter '{p}' (or just enter to quit): ")
            if not v:
                break

            params.append({p: v})
       
        # construct the command message to send to the server        
        b.send_event(src = orover.controller.remote_interface
                    ,reason = b.name_to_enum(command)
                    ,prio = orover.priority.low
                    ,body = json.dumps(params)
                    )
        


if __name__ == "__main__":
    main()