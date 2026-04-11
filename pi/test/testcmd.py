#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r -> object recognition and versatile exploration robot
     License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description: Allow testing of the BOSS server with command-line tool
"""

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

    print("Starting test command tool...")
    print("\033[1;31mThis tool does not check the validity of the commands or parameters, so use with caution!\033[0m")
    
    b = base()
    while True:

        printlist()
        print("")
        command = input("\033[0;0mEnter command (or 'exit' to quit): ")

        if command.lower() == 'exit':
            print("Exiting test command tool.")
            break
 
        param_values = ""  
        while True:
            param_name = input("Enter parameter name (or 'done' to finish): ")
            if param_name.lower() == 'done':
                break
            param_value = input(f"Enter value for parameter '{param_name}': ")
            param_values += f"\"{param_name}\": \"{param_value}\", "

        # Remove trailing comma and space if parameters were added
        if param_values:
            param_values = param_values[:-2]  # Remove last ", "
            
        print(f"Sending: {command}, parameters: {param_values}")
       
        # construct the command message to send to the server        
        b.send_event(src = orover.controller.remote_interface
                    ,reason = orover.cmd[command]
                    ,body = "{" + param_values + "}" if param_values else ""
                    )
        
    b.terminate(0,0)

if __name__ == "__main__":
    main()