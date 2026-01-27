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

from email import message
import json
import uuid


class tell:
    """Robot command, state, and event enumeration class"""
    
    # System Commands
    class System:
        start                       =  100
        stop                        =  101
        pause                       =  102
        resume                      =  103
        shutdown                    =  104
        reboot                      =  105
        reset                       =  106
        set                         =  107
    
    # Motion Commands
    class Motion:
        move                        =  200
        moveTo                      =  201
        rotate                      =  202
        setVelocity                 =  203
        stopMotion                  =  204
        dock                        =  205
        undock                      =  206
    
    # Actuator Commands
    class Actuator:
        setPosition                 =  300
        setSpeed                    =  301
        setTorque                   =  302
        open                        =  303
        close                       =  304
        enable                      =  305
        disable                     =  306
    
    # Sensor Commands
    class Sensor:
        calibrate                   =  400
        startStream                 =  401
        stopStream                  =  402
        setRate                     =  403
        setRange                    =  404
    
    # Config Commands
    class Config:
        setParam                    =  500
        getParam                    =  501
        loadProfile                 =  502
        saveProfile                 =  503
    
    # System State
    class SystemState:
        mode                        =  600
        lifecycle                   =  601
        health                      =  602
        uptime                      =  603
    
    # Motion State
    class MotionState:
        pose                        =  700
        velocity                    =  701
        goal                        =  702
        motion                      =  703
    
    # Power State
    class PowerState:
        battery                     =  800
        charging                    =  801
        powerSource                 =  802
        temperature                 =  803
    
    # Actuator State
    class ActuatorState:
        position                    =  900
        speed                       =  901
        enabled                     =  902
        load                        =  903
    
    # Sensor State
    class SensorState:
        sensorStatus                = 1000
        lastUpdate                  = 1001
        signalQuality               = 1002
    
    # Safety Events
    class SafetyEvent:
        emergencyStop               = 1100
        collisionDetected           = 1101
        obstacleDetected            = 1102
        overcurrent                 = 1103
        overtemperature             = 1104
        lowBattery                  = 1105
    
    # System Events
    class SystemEvent:
        startupComplete             = 1200
        shutdownInitiated           = 1201
        modeChanged                 = 1202
        faultRaised                 = 1203
        faultCleared                = 1204
    
    # Task Events
    class TaskEvent:
        goalReached                 = 1300
        goalFailed                  = 1301
        docked                      = 1302
        undocked                    = 1303
    
    # Vision Events
    class VisionEvent:
        objectDetected              = 1400
        pathBlocked                 = 1401
        markerDetected              = 1402
        humanDetected               = 1403
        lineLost                    = 1404
    
    # External Events
    class ExternalEvent:
        manualOverride              = 1500
        remoteCommand               = 1501
        heartbeatTimeout            = 1502
        configChanged               = 1503

    # Message priority levels
    class priority:
        low                         = 1
        normal                      = 5
        high                        = 10

    def toboss(socket, data):
        """Placeholder function to send message to the boss system.
           Expecting json-serializable dictionary as input."""
    
        # Check if the data is a dictionary
        if not isinstance(data, dict):
            print (f" {data} is not a dictionary type")
            return False
        
        if "source" not in data:
            print (f"JSON message: {data} does not contain 'source' field")
            return False
        source_value = data.get("source")
    
        if "priority" not in data:
            prio_value = tell.priority.low
        else:
            prio_value = data.get("priority")
            if not prio in tell.priority.__dict__.values():
                print (f"JSON message: {data} has invalid 'priority' field")
                return False    
    
        if "type" not in data:
            print (f"JSON message: {data} does not contain 'type' field")
            return False
        type_value = data.get("type")
# check removed for type validity, needs more thought
#        if not type_value in tell.__dict__.values():
#            print (f"JSON message: {data} has invalid 'type' field")
#            return False
        
        if "value" not in data:
            print (f"JSON message: {data} does not contain 'value' field")
            return False
        value_field = data.get("value") 
    
        # Construct the message to send to the boss
        msg = {"msg_id" : str(uuid.uuid4())
               , "source": source_value
               , "priority": prio_value
               , "type": type_value
               , "value": {"distance" : value_field}
              } 
        socket.send((json.dumps(msg).encode('utf-8')))
        answer = socket.recv()
        return answer
    
 