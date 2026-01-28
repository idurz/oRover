#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File orover_lib.py
Copyright (C) 2026 C v Kruijsdijk & P. Zengers
License: MIT License
Created: 2026-01-27
Description:
    Language definitions for robot commands, states, and events.
"""

from datetime import datetime
import configparser, os, sys, uuid, json

# -----------------------------------------
# --- Declare some globals ----------------
# -----------------------------------------

configfile_name = 'config.ini' # Where to find the global configuration
config = None   # No config retrieved yet

def readConfig():
    # Read all info from config.ini

    if not os.path.isfile(configfile_name):
        sys.exit("Configuration file does not exist")

    config = configparser.ConfigParser() 
    config.read(configfile_name)
    return config

# -----------------------------------------
# --- Robot Language Definitions ---
# -----------------------------------------

class priority:
    """Robot message priority levels enumeration class"""

    low                             =    1 # Low priority, background messages
    normal                          =    5 # Normal priority, standard messages
    high                            =   10 # High priority, only for critical messages


class origin:
    """Robot known message sources enumeration class"""

    # Sensors
    class sensor:
        ultrasonic_front            = 1001
        ultrasonic_rear             = 1002
        ultrasonic_left             = 1003
        ultrasonic_right            = 1004
        lidar                       = 1010
        camera_front                = 1020
        camera_rear                 = 1021
        imu                         = 1030
        gps                         = 1040
        wheel_encoder_left          = 1050
        wheel_encoder_right         = 1051
        temperature                 = 1060
        battery                     = 1070

    # Actuators
    class actuator:
        left_wheel_motor            = 2000
        right_wheel_motor           = 2001
        arm_joint_1                 = 2010
        arm_joint_2                 = 2011
        gripper                     = 2020

    class controller:
        motion_controller           = 3000
        power_manager               = 3010
        safety_system               = 3020
        vision_system               = 3030
        navigation_system           = 3040
        path_planner                = 3050 
        remote_interface            = 3060
    

class tell:
    """Robot command, state, and event enumeration class"""
    
    # System Commands
    class System:
        start                       = 3000  # Start robot operation
        stop                        = 3001  # Stop robot operation controlled
        pause                       = 3002  # Freeze all actions
        resume                      = 3003  # Resume after pause
        shutdown                    = 3004  # Shutdown robot software
        reboot                      = 3005  # Reboot robot systems
        reset                       = 3006  # Reset faults and continue operation

    # Motion Commands
    class Motion:
        move                        = 3100  # Move to relative position
        moveTo                      = 3101  # Move to absolute position
        rotate                      = 3102  # Rotate to relative angle in place
        setVelocity                 = 3103  # Set constant velocity
        stopMotion                  = 3104  # Stop all motion immediately
        dock                        = 3105  # Dock to charging station
        undock                      = 3106  # Undock from charging station

    # Actuator Commands
    class Actuator:
        setPosition                 = 3200  # Set actuator position for servo or arm joint
        setSpeed                    = 3201  # Set actuator motor speed
        setTorque                   = 3202  # Set actuator torque
        open                        = 3203  # Open gripper or valve
        close                       = 3204  # Close gripper or valve
        enable                      = 3205  # Power on actuator
        disable                     = 3206  # Power off actuator

    # Sensor Commands
    class Sensor:
        calibrate                   = 3300  # Calibrate sensor
        startStream                 = 3301  # Enable streaming sensor data
        stopStream                  = 3302  # Disable streaming sensor data
        setRate                     = 3303  # Set sensor sampling rate
        setRange                    = 3304  # Set sensor measurement range  

    # Config Commands
    class Config:
        setParam                    = 3400 # Set configuration parameter
        getParam                    = 3401 # Get configuration parameter
        loadProfile                 = 3402 # Load configuration profile
        saveProfile                 = 3403 # Save configuration profile

    # System State
    class SystemState:
        mode                        = 4000  # Returns manual, autonomous, safe, maintenance
        lifecycle                   = 4001  # Returns current lifecycle state: initializing, running, stopping, stopped
        health                      = 4002  # Returns overall system health status: ok, degraded, fault
        uptime                      = 4003  # Returns system uptime in seconds

    # Motion State
    class MotionState:
        pose                        = 4100 # Returns current position and orientation, x, y, theta
        velocity                    = 4101 # Returns current linear and angular velocity
        goal                        = 4102 # Returns current motion goal or target
        motion                      = 4103 # Returns current motion status: idle, moving, rotating, docking

    # Power State
    class PowerState:
        battery                     = 4200 # Returns current battery level percentage and voltage
        charging                    = 4201 # Returns charging status: true or false
        powerSource                 = 4202 # Returns current power source: battery, external, solar
        temperature                 = 4203 # Returns current battery temperature in Celsius

    # Actuator State
    class ActuatorState:
        position                    = 4300 # Returns current actuator position joint angles or linear position
        speed                       = 4301 # Returns current actuator speed rpm or linear speed
        enabled                     = 4302 # Returns current actuator enabled status true or false
        load                        = 4303 # Returns current actuator load torque and current

    # Sensor State
    class SensorState:
        sensorStatus                = 4400 # Returns current sensor status: ok, error, calibrating, offline
        lastUpdate                  = 4401 # Returns timestamp of last sensor data update
        signalQuality               = 4402 # Returns current sensor signal quality metric
        dataRate                    = 4403 # Returns current sensor data rate in Hz

    # Safety Events
    class SafetyEvent:
        emergencyStop               = 5000 # Emergency stop activated
        collisionDetected           = 5001 # Collision detected
        obstacleDetected            = 5002 # Obstacle detected, to close to path
        overcurrent                 = 5003 # Overcurrent detected, motor overload
        overtemperature             = 5004 # Overtemperature detected, too hot
        lowBattery                  = 5005 # Critical low battery detected
    
    # System Events
    class SystemEvent:
        startupComplete             = 5100 # System startup completed, oRover ready
        shutdownInitiated           = 5101 # System shutdown initiated
        modeChanged                 = 5102 # System mode changed
        faultRaised                 = 5103 # System fault raised
        faultCleared                = 5104 # System fault cleared
    
    # Task Events
    class TaskEvent:
        goalReached                 = 5200 # Navigation target reached
        goalFailed                  = 5201 # Navigation target failed
        docked                      = 5202 # Successfully docked
        undocked                    = 5203 # Successfully undocked

    # Vision Events
    class VisionEvent:
        objectDetected              = 5300 # Object detected in vision system
        pathBlocked                 = 5301 # Route blocked by obstacle
        markerDetected              = 5302 # Marker detected in vision system
        humanDetected               = 5303 # Human detected in vision system
        lineLost                    = 5304 # Line lost in vision system
    # External Events
    class ExternalEvent:
        manualOverride              = 5400 # Manual override activated, operator took control
        remoteCommand               = 5401 # Remote command received from external system
        heartbeatTimeout            = 5402 # Heartbeat timeout detected, lost connection
        configChanged               = 5403 # Configuration changed



# -----------------------------------------
# --- Utility Functions from tell class ---
# -----------------------------------------

    def toboss(socket, data):
        """"        Send a message to the BOSS via the provided socket.
        Args:
            socket: zmq socket connected to the BOSS
            data: dictionary containing the message fields:
                - source (str): source of the message
                - priority (int, optional): priority level of the message
                - type (int): type of the message
                - value (any): value associated with the message
        Returns:
            The response received from the BOSS.
                False            if the data is invalid, no action taken, 
                True             if the message was sent successfully
            
        """
    
        # Check if the data is a dictionary
        if not isinstance(data, dict):
            print (f"{data} is not a dictionary type")
            return False
        
        for field in ["src", "type", "body"]:
            if field not in data:
                print (f"{data} does not contain '{field}' field")
                return False
            
        source_value = data.get("src")
        type_value = data.get("type")
        body_field = data.get("body") 

        if "value" not in body_field:
            print (f"{data} does not contain 'value' field in 'body'")
            return False
        else:
            value_field = body_field.get("value")   

        prio_value = data.get("prio", priority.low)
        if prio_value not in priority.__dict__.values():
            print (f"{data} has invalid 'prio' field")
            return False    

        # Construct the message to send to the boss
        msg = {"id"  : str(uuid.uuid4()),
               "ts"  : datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
               "src" : source_value,
               "prio": prio_value,
               "type": type_value,
               "body": {"value" : value_field}
              } 
        
        socket.send((json.dumps(msg).encode('utf-8')))
        answer = socket.recv()

        return answer
    
 