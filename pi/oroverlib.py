#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  ibrary of constants and definitions for the ROVER BOSS system
"""

import argparse
import configparser
from enum import IntEnum, unique
import logging, logging.handlers
import os
import sys

# Read configuration from config.ini file.
def readConfig(name_requested=False):

    # Check if config file is given as argument, otherwise use default
    parser = argparse.ArgumentParser(description=f"Object Recognition and Versatile Exploration Robot")
    parser.add_argument("--config", default="config.ini"
                       ,help="Path to configuration file (default: config.ini)")  
    args = parser.parse_args()

    # Check if config file exists, otherwise exit with error
    if not os.path.isfile(args.config):
        sys.exit(f"Configuration file {args.config} does not exist")

    # Read configuration from config.ini file
    config = configparser.ConfigParser() 
    config.read(args.config)
    
    if name_requested:
        return config, args.config
    else:
        return config




# Returns the name of the current module, based on the filename of the script, or the name defined in the config file if it matches the current script name. This allows for more flexible naming of processes in the config file
def getmodulename(config):
    
    if sys.argv[0] in config.items('scripts'):
        # find item in config that matches the current script name and return the key (name) of that item
        for name, path in config.items('scripts'):
            if sys.argv[0] == os.path.basename(path):
                return name
        return "default"  # default name if not found in config
    return sys.argv[0].split('.')[0]


# Set up logging to send log messages to the boss process via a socket handler
def setlogger(config):
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler('localhost',
                     logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    rootLogger.addHandler(socketHandler)
    logger = logging.getLogger(getmodulename(config))

    loglevel = config.get('orover','loglevel',fallback="UNKNOWN").upper()
    known_level = (loglevel in ["DEBUG","INFO","WARNING","ERROR","CRITICAL"])
    if not known_level:
        logger.setLevel("ERROR")
        logger.error((f"Invalid log level {loglevel} in config, defaulting to 'ERROR'"))
    else:
        logger.setLevel(loglevel.upper())
    
    return logger



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
class operational_mode(IntEnum):
    """Robot operational modes enumeration."""
    idle                               =  100 # Idle mode, minimal activity, waiting for commands
    active                             =  101 # Active mode, performing tasks and operations
    maintenance                        =  102 # Maintenance mode, for diagnostics and repairs

@unique
class lifecycle_stage(IntEnum):
    """Robot lifecycle stages enumeration."""
    startup                            =  200 # Startup stage, initializing systems and preparing for operation
    running                            =  201 # Running stage, normal operation and task execution
    shutdown                           =  202 # Shutdown stage, safely powering down systems and preparing for transport or storage

@unique
class power_source(IntEnum):
    """Robot power sources enumeration."""
    battery                            =  300 # Battery power source, providing energy for mobility and operations
    mains                              =  301 # Mains power source, for stationary operation or charging
    solar                              =  302 # Solar power source, utilizing solar panels for energy generation

@unique
class health_status(IntEnum):
    """Robot health status enumeration."""
    healthy                            =  400 # Healthy status, all systems functioning properly
    warning                            =  401 # Warning status, potential issues detected that may require attention
    critical                           =  402 # Critical status, significant issues detected that require immediate attention to prevent damage or failure

@unique
class origin(IntEnum):
    """Robot known message sources grouped as Enums."""
    heartbeat                          = 1000
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
    sensor_collision_front             = 1080   
    sensor_collision_rear              = 1081
    sensor_collision_top               = 1082
    test_message                       = 1090 
    
@unique
class actuator(IntEnum):
    motor_wheels                       = 2000
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
    set_motor_speed                    = 4107

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
    heartbeat                          = 6402
    configChanged                      = 6403
    test_message                       = 6499