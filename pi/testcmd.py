#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r -> object recognition and versatile exploration robot
     License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description: Allow testing of the BOSS server with command-line tool
"""

import oroverlib as orover
import logger

availalable_commands = [
    {"name":"start",           "description": "Start the robot's main functions and operations",
                               "param": {}} ,
    {"name":"stop",            "description": "Stop the robot's main functions and operations",
                               "param": {}},
    {"name":"pause",           "description": "Pause the robot's current activities, allowing for temporary halts without shutting down completely",
                               "param": {}},
    {"name":"resume",          "description": "Resume the robot's activities after a pause, allowing it to continue from where it left off",
                               "param": {}},
    {"name":"shutdown",        "description": "Safely shut down the robot, powering down all systems and preparing for transport or storage",
                               "param": {}},
    {"name":"reboot",          "description": "Reboot the robot, restarting all systems and processes without a full shutdown",
                               "param": {}},
    {"name":"reset",           "description": "Reset the robot's state, clearing any errors or faults and returning to a known baseline condition",
                               "param": {}},
    {"name":"move",            "description": "Move the robot in a specified direction and distance, typically used for navigation and positioning",
                               "param": {"direction": "Direction to move (e.g., forward, backward, left, right)",
                                         "distance": "Distance to move in centimeters"}},
    {"name":"moveTo",          "description": "Move the robot to a specific location or coordinate",
                               "param": {}},
    {"name":"rotate",          "description": "Rotate the robot by a specified angle",
                               "param": {}},
    {"name":"setVelocity",     "description": "Set the robot's velocity",
                               "param": {}},
    {"name":"stopMotion",      "description": "Stop all motion of the robot",
                               "param": {}},
    {"name":"dock",            "description": "Dock the robot to a charging station or docking point",
                               "param": {}},
    {"name":"undock",          "description": "Undock the robot from a charging station or docking point",
                               "param": {}},
    {"name":"set_motor_speed", "description": "Set the speed of the robot's motors, allowing for precise control over movement and acceleration",
                               "param": {}},
    {"name":"setPosition",     "description": "Set the position of an actuator, such as a robotic arm joint or camera pan/tilt mechanism",
                               "param": {}},
    {"name":"setSpeed",        "description": "Set the speed of an actuator, such as a robotic arm joint or camera pan/tilt mechanism",
                               "param": {}},
    {"name":"setTorque",       "description": "Set the torque of an actuator, such as a robotic arm joint or gripper",
                               "param": {}},
    {"name":"open",            "description": "Open an actuator, such as a gripper or camera pan/tilt mechanism",
                               "param": {}},
    {"name":"close",           "description": "Close an actuator, such as a gripper or camera pan/tilt mechanism",
                               "param": {}},
    {"name":"enable",          "description": "Enable an actuator, such as a robotic arm joint or camera pan/tilt mechanism",
                               "param": {}},
    {"name":"disable",         "description": "Disable an actuator, such as a robotic arm joint or camera pan/tilt mechanism",
                               "param": {}},
]


def printlist():
    print("")
    print("Available commands:")
    print("------------------")
    for cmd in availalable_commands:
        print(f"\033[0;32m{cmd['name']} - {cmd['description']}")


def main():

    print("Starting test command tool...")
    print("\033[1;31mThis tool doe not check the validity of the commands or parameters, so use with caution!\033[0m")
    socket = orover.connect_to_server()

    while True:

        printlist()
        print("")
        command = input("\033[0;0mEnter command (or 'exit' to quit): ")

        if command.lower() == 'exit':
            print("Exiting test command tool.")
            break

        # Find the command in the available commands list
        cmd_info = next((cmd for cmd in availalable_commands if cmd['name'] == command), None)
        if not cmd_info:
            print("")
            print(f"Invalid command: {command}. Please try again.")
            continue

        params = {}
        # Check parameters if needed
        if cmd_info['param']:
            for param_name, param_desc in cmd_info['param'].items():
                param_value = input(f"Enter value for {param_name} ({param_desc}): ")
                params[param_name] = param_value 

            # Here you would construct the command message with the parameters
            # For example, you could create a JSON message to send to the server
            # command_message = json.dumps(params)
        print(f"Sending: {cmd_info['name']}, parameters: {params if cmd_info['param'] else 'None'}  ")
        logger.info(f"Sending command: {cmd_info['name']} with parameters: {params if cmd_info['param'] else 'None'}")
        
        # construct the command message to send to the server
        
        a = orover.get_name(orover.cmd[cmd_info['name']])
        answer = orover.send(socket
                            ,src = orover.controller.remote_interface
                            ,reason = orover.cmd[cmd_info['name']]
                            ,body = params
                            )
        print(f"\033[1;31mReceived response: {answer}\033[0m")

    orover.disconnect_from_server(socket)

if __name__ == "__main__":
    main()