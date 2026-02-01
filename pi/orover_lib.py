#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""  #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
    #     #   R     R   #      #   V     V   E         R     R
    #     #   R     R   #      #    V   V    E         R     R
    #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
    #     #   R   R     #      #     VV      E         R   R
     #####    R    R     ######      VV      EEEEEEE   R    R  

   License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
   Created:     2026-01-27
   Description: Library of constants and definitions for the ROVER BOSS system"""

import zmq # pyright: ignore[reportMissingImports]
from datetime import datetime
from enum import IntEnum, unique
import configparser, os, sys, uuid, json

# -------------------------------------------------
# ----- Declare some global var and functions -----
# -------------------------------------------------


configfile_name = 'config.ini' # Where to find the global configuration
config = None   # No config retrieved yet


def readConfig():
    """ Read configuration from config.ini file.
    Returns:
        ConfigParser object with configuration data.
    Raises:
        SystemExit: if the configuration file does not exist.   
    """
    if not os.path.isfile(configfile_name):
        sys.exit("Configuration file does not exist")

    config = configparser.ConfigParser() 
    config.read(configfile_name)
    return config


def get_name(val):
    """Return the best-effort name for a numeric type.
       Reverse lookup through cmd, state, event enums.
       Arguments:
           val: numeric value to lookup
       Returns:
           Name of the matching enum member, or str(val) if not found
    """
    for cls in (cmd, state, event, origin, actuator, controller, priority):
        try:
            return cls(val).name
        except Exception:
            pass
    return str(val)


def connect_to_server():
    """Connect to BOSS server via ZMQ
    Args:
        None

    Returns:
        ZMQ socket or None when socket connect was not succesfull

    Raises:
        sys.exit on errors
    """
    config = readConfig()
    try:
        context = zmq.Context()
        context.setsockopt(zmq.SNDTIMEO,config.getint('boss','send_timeout',fallback=2500))
        context.setsockopt(zmq.RCVTIMEO,config.getint('boss','receive_timeout',fallback=2500))
    except Exception as e: 
        sys.exit(f"Could not create ZMQ context. Exception {e}" )
    
    try:
        socket = context.socket(zmq.REQ)
        socket.connect(config.get('boss','client_socket'))
    except Exception as e: 
        sys.exit(f"Could not connect to BOSS. Exception {e}" )

    return socket


def disconnect_from_server(socket):
    """Disconnects client from the boss server
    Args:
        socket:  zmq socket connected to the BOSS
    Returns:
        nothing
    """
    socket.close()


def send(socket,src,type,body={},prio=None):
    """Send a message to the BOSS via the provided socket.
    Args:
        socket:  zmq socket connected to the BOSS
        src:     who is sending the the message
        me       script file where the message originates from
        type     type of the message
        body     optional parameteres
        prio (optional): priority level of the message

    Returns:
        The response received from the BOSS.
            False            if the data is invalid, no action taken, 
            True             if the message was sent successfully
    Raises:
        None    
    """

    # Check if src is an instance of one of the allowed enums
    if not isinstance(src, (origin, actuator, controller)):
        print (f"Invalid 'src' field, must be known enum ({src})")
        return False
    
    if not isinstance(type, (cmd, state, event)):
        print (f"Invalid 'type' field must be known enum ({type})")
        return False

    # check if body is valid json
    body_field = body
    if isinstance(body, str):
        try:
            body_field = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            print (f"{body} is not valid JSON")
            return False

    # priority: accept an int or Priority member
    
    if prio is None:
        prio = priority.normal
    if not isinstance(prio,priority):
        print (f"Invalid 'prio' field must be known enum ({prio})")
        return False    

    # Construct the message to send to the boss
    msg = {"id"  : str(uuid.uuid4())
          ,"ts"  : datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
          ,"src" : src
          ,"me"  : os.path.basename(__file__)
          ,"prio": prio
          ,"type": type
          ,"body": body_field
          } 

    socket.send_json(msg)
    try:
        answer = socket.recv()
    except Exception as e: 
        print(f"Receiving ZMQ anwer failed with exception {e}") 
        return False

    return answer
    

# -----------------------------------------
# --- Robot Language Definitions ---
# -----------------------------------------


@unique
class priority(IntEnum):
    """Robot message priority levels enumeration."""
    low                                =    1  # Low priority, background messages
    normal                             =    5  # Normal priority, standard messages
    high                               =   10  # High priority, only for critical messages

@unique
class origin(IntEnum):
    """Robot known message sources grouped as Enums."""
    sensor_ultrasonic_front            = 1001
    sensor_ultrasonic_rear             = 1002
    sensor_ultrasonic_left             = 1003
    sensor_ultrasonic_right            = 1004
    sensor_lidar                       = 1010
    sensor_camera_front                = 1020
    sensor_camera_rear                 = 1021
    sensor_imu                         = 1030
    sensor_gps                         = 1040
    sensor_wheel_encoder_left          = 1050
    sensor_wheel_encoder_right         = 1051
    sensor_temperature                 = 1060
    sensor_battery                     = 1070

@unique
class actuator(IntEnum):
    left_wheel_motor                   = 2000
    right_wheel_motor                  = 2001
    arm_joint_1                        = 2010
    arm_joint_2                        = 2011
    gripper                            = 2020

@unique
class controller(IntEnum):
    motion_controller                  = 3000
    power_manager                      = 3010
    safety_system                      = 3020
    vision_system                      = 3030
    navigation_system                  = 3040
    path_planner                       = 3050
    remote_interface                   = 3060



@unique
class cmd(IntEnum):
    """Robot command, state, and event enumeration class (grouped Enums)."""
    start                              = 4000
    stop                               = 4001
    pause                              = 4002
    resume                             = 4003
    shutdown                           = 4004
    reboot                             = 4005
    reset                              = 4006

    move                               = 4100
    moveTo                             = 4101
    rotate                             = 4102
    setVelocity                        = 4103
    stopMotion                         = 4104
    dock                               = 4105
    undock                             = 4106

    setPosition                        = 4200
    setSpeed                           = 4201
    setTorque                          = 4202
    open                               = 4203
    close                              = 4204
    enable                             = 4205
    disable                            = 4206

    calibratesensor                    = 4300
    startStream                        = 4301
    stopStream                         = 4302
    setRate                            = 4303
    setRange                           = 4304

    getParam                           = 4400
    setParam                           = 4401
    loadProfile                        = 4402
    saveProfile                        = 4403

@unique
class state(IntEnum):
    system_mode                        = 5000
    system_lifecycle                   = 5001
    system_health                      = 5002
    system_uptime                      = 5003

    pose                               = 5100
    velocity                           = 5101
    goal                               = 5102
    motion                             = 5103

    battery                            = 5200
    charging                           = 5201
    power_source                       = 5202
    power_temperature                  = 5203

    actuator_speed                     = 5301
    actuator_enabled                   = 5302
    actuator_load                      = 5303

    sensor_status                      = 5400
    sensor_lastupdate                  = 5401
    sensor_signalquality               = 5402
    sensor_datarate                    = 5403

@unique
class event(IntEnum):
    emergencyStop                      = 6000
    collisionDetected                  = 6001
    obstacleDetected                   = 6002
    overcurrent                        = 6003
    overtemperature                    = 6004
    lowBattery                         = 6005

    startupComplete                    = 6100
    shutdownInitiated                  = 6101
    modeChanged                        = 6102
    faultRaised                        = 6103
    faultCleared                       = 6104

    goalReached                        = 6200
    goalFailed                         = 6201
    docked                             = 6202
    undocked                           = 6203

    object_detected                    = 6300
    pathBlocked                        = 6301
    marker_detected                    = 6302
    human_detected                     = 6303
    lineLost_detected                  = 6304

    manualOverride                     = 6400
    remoteCommand                      = 6401
    heartbeatTimeout                   = 6402
    configChanged                      = 6403

    #all_commands = {m.value: m for grp in (cmd.system, cmd.motion, cmd.actuator, cmd.sensor, cmd.config) for m in grp}
    #all_states   = {m.value: m for grp in (state.system, state.motion, state.power, state.actuator, state.sensor) for m in grp}
    #all_events   = {m.value: m for grp in (event.safety, event.system, event.task, event.detected, event.external) for m in grp}
    #all_tells    = {**all_commands, **all_states, **all_events}


 