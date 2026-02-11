# Enumeration

## Background
The oRover system sends messages back and forth true its [message bus](eventbus.md). To ease up communication, prevent typos and text comparisions messages are using constants - enumerations for parts of the message where possible. This goes for the priority (prio), the origin, actuator, controller, commands (cmd), states and events. 

# Usage

An enumeration looks like a dotted text string. Internal python translates it to numeric items to ease up compaerisons. See [class enum](https://docs.python.org/3/library/enum.html#enum.IntEnum)

Example usage:

```
orover.publish(socket
              ,src | orover.origin.sensor_ultrasonic_front 
              ,reason | orover.event.object_detected
              ,body | {"distance": 20.0})
```

Note that an enumeration always has two or three components: `'library'.'class'.'value'` as shown in the example. Here we assume that the libary orover_lib is named `orover` in the code as per standard in each script. 

```
import orover_lib as orover
```

## Known enumerations

This section contains the known enumerations and the explanation

### Enumeration for priority

| Value                      | Robot message priority levels                                        |
|----------------------------|----------------------------------------------------------------------|
| low                        | Low priority, background messages                                    |
| normal                     | Normal priority, standard messages                                   |
| high                       | High priority, only for critical messages                            |

### Enumeration for operational mode

| Value                      | Robot operational modes                                              |
|----------------------------|----------------------------------------------------------------------|
| idle                       | Idle mode, minimal activity, waiting for commands                    |
| active                     | Active mode, performing tasks and operations                         |
| maintenance                | Maintenance mode, for diagnostics and repairs                        |

### Enumeration for lifecycle

| Value                      | Robot lifecycle stages                                               |
|----------------------------|----------------------------------------------------------------------|
| startup                    | Startup stage, initializing systems and preparing for operation      |
|running                     | Running stage, normal operation and task execution                   |
| shutdown                   | Shutdown stage, safely powering down systems and preparing for transport or storage |

### Enumeration for power source:

| Value                      | Robot power source                                                   |
|----------------------------|----------------------------------------------------------------------|
| battery                    | Battery power source, providing energy for mobility and operations   |
| mains                      | Mains power source, for stationary operation or charging             |
| solar                      | Solar power source, utilizing solar panels for energy generation     |

### Enumeration for health status:

| Value                      | Robot health status                                                  |
|----------------------------|----------------------------------------------------------------------|
| healthy                    | Healthy status, all systems functioning properly                     |
| warning                    | Warning status, potential issues detected that may require attention |
| critical                   | Critical status, significant issues detected that require immediate attention to prevent damage or failure |

### Enumeration for origin:

| Value                      | Robot known message sources                                          |
|----------------------------|----------------------------------------------------------------------|
| heartbeat                  | Heartbeat signal from system parts                                   |
| sensor_ultrasonic_front    | Front ultrasonic sensor reading                                      |
| sensor_ultrasonic_rear     | Rear ultrasonic sensor reading                                       |
| sensor_ultrasonic_left     | Left ultrasonic sensor reading                                       |
| sensor_ultrasonic_right    | Right ultrasonic sensor reading                                      |
| sensor_lidar               | LIDAR sensor reading                                                 |
| sensor_camera_front        | Front camera image data                                              |
| sensor_camera_rear         | Rear camera image data                                               |
| sensor_imu                 | IMU sensor data (acceleration, orientation)                          |
| sensor_gps                 | GPS sensor data (latitude, longitude, altitude)                      |
| sensor_wheel_encoder_left  | Left wheel encoder data                                              |
| sensor_wheel_encoder_right | Right wheel encoder data                                             |
| sensor_temperature         | Temperature sensor reading                                           |
| sensor_battery             | Battery level sensor reading                                         |
| sensor_collision_front     | Physical collision detected front                                    |
| sensor_collision_rear      | Physical collision detected rear                                     |
| sensor_collision_top       | Physical collision detected top                                      |
    
### Enumeration for actuator:

| Value                      | Robot known actuators and motors                                     |
|----------------------------|----------------------------------------------------------------------|
| motor_wheels               | Main drive motors for wheels or tracks                               |
| arm_joint_1                | First joint of the robotic arm                                       |
| arm_joint_2                | Second joint of the robotic arm                                      |
| gripper                    | Gripper actuator for picking up objects                              |
| camera_pan                 | Pan mechanism for camera                                             |
| camera_tilt                | Tilt mechanism for camera                                            |

### Enumeration for controller:

| Value                      | Robot known controllers (making decisions)                           |
|----------------------------|----------------------------------------------------------------------|
| motion_controller          | Main motion control system for navigation and movement               |
| power_manager              | Power management system for battery and energy distribution          |
| safety_system              | Safety system for collision avoidance and emergency stops            |
| vision_system              | Computer vision system for object recognition and tracking           |
| navigation_system          | Navigation system for path planning and localization                 |
| path_planner               | Path planning module for determining optimal routes                  |
| remote_interface           | Remote control interface for receiving commands from external sources |

### Enumeration for commamnds:

| Value                      | Robot known commands (cmd)                                           |
|----------------------------|----------------------------------------------------------------------|
| start                      | Start the robot's main functions and operations                      |
| stop                       | Stop the robot's main functions and operations                       |
| pause                      | Pause the robot's current activities, allowing for temporary halts without shutting down completely |
| resume                     | Resume the robot's activities after a pause, allowing it to continue from where it left off |
| shutdown                   | Safely shut down the robot, powering down all systems and preparing for transport or storage |
| reboot                     | Reboot the robot, restarting all systems and processes without a full shutdown |
| reset                      | Reset the robot's state, clearing any errors or faults and returning to a known baseline condition |
| move                       | Move the robot in a specified direction and distance, typically used for navigation and positioning |
| moveTo                     | Move the robot to a specific location or coordinate                  |
| rotate                     | Rotate the robot by a specified angle                                |
| setVelocity                | Set the robot's velocity                                             |
| stopMotion                 | Stop all motion of the robot                                         |
| dock                       | Dock the robot to a charging station or docking point                |
| undock                     | Undock the robot from a charging station or docking point            |
| set_motor_speed            | Set the speed of the robot's motors, allowing for precise control over movement and acceleration |
| setPosition                | Set the position of an actuator, such as a robotic arm joint or camera pan/tilt mechanism |
| setSpeed                   | Set the speed of an actuator, such as a robotic arm joint or camera pan/tilt mechanism
| setTorque                  | Set the torque of an actuator, such as a robotic arm joint or gripper |
| open                       | Open an actuator, such as a gripper or camera pan/tilt mechanism     |
| close                      | Close an actuator, such as a gripper or camera pan/tilt mechanism    |
| enable                     | Enable an actuator, such as a robotic arm joint or camera pan/tilt mechanism |
| disable                    | Disable an actuator, such as a robotic arm joint or camera pan/tilt mechanism |
| calibratesensor            | Calibrate a specific sensor, to ensure accurate readings and performance |
| startStream                | Start streaming data from a camera or LIDAR, allowing for real-time monitoring |
| stopStream                 | Stop streaming data from a camera or LIDAR                           |
| setRate                    | Set the data update rate for a specific sensor, such as an ultrasonic sensor or IMU |
| setRange                   | Set the detection range for a specific sensor, such as an ultrasonic sensor or LIDAR |
| getParam                   | Get a specific parameter or setting from the robot's system, such as a configuration value or status information |
| setParam                   | Set a specific parameter or setting in the robot's system, such as a configuration value or operational mode |
| loadProfile                | Load a predefined profile or configuration for the robot, such as a set of parameters for a specific task or environment |
| saveProfile                | Save the current profile or configuration of the robot, such as a set of parameters for a specific task or environment |

### Enumeration for states:

| Value                      | Robot known states                                                   |
|----------------------------|----------------------------------------------------------------------|
| system_mode                | Current operational mode of the robot, see class operational_mode for possible values |
| system_lifecycle           | Current lifecycle stage of the robot, see class lifecycle_stage for possible values |
| system_health              | Current health status of the robot, see class health_status for possible values |
| system_uptime              | Total time the robot has been operational since last startup         |
| pose                       | Current position and orientation of the robot in its environment     |
| velocity                   | Current speed and direction of the robot's movement                  |
| goal                       | Current navigation goal or target position for the robot             |
| motion                     | Current motion state or command of the robot (e.g., moving, stopped, turning) |
| battery                    | Current battery level or status of the robot                         |
| charging                   | Charging status of the robot's battery                               |
| power_source               | Current power source being used by the robot, see class power_source for possible values |
| power_temperature          | Current temperature of the robot's power system, indicating potential overheating issues |
| actuator_speed             | Current speed of the robot's actuators                               |
| actuator_enabled           | Whether the robot's actuators are enabled or disabled                |
| actuator_load              | Current load or effort being exerted by the robot's actuators        |
| sensor_status              | Current status of the robot's sensors                                |
| sensor_lastupdate          | Timestamp of the last sensor data update                             |
| sensor_signalquality       | Quality of the sensor signals being received                         |
| sensor_datarate            | Data rate at which sensor information is being transmitted           |

### Enumeration for events:

| Value                      | Robot known events                                                   |
|----------------------------|----------------------------------------------------------------------|
| emergencyStop              | Emergency stop activated, requiring immediate halt                   |
| collisionDetected          | Physical collision detected by the robot's sensors                   |
| obstacleDetected           | Obstacle detected in the robot's path, requires actionto avoid a collision |
| overcurrent                | Overcurrent condition detected in the robot's electrical system      |
| overtemperature            | Overtemperature condition detected in the robot's systems            |
| lowBattery                 | Low battery level detected, indicating that the robot's battery has reached a critical level |
| startupComplete            | Startup complete, indicating that the robot has successfully completed its startup sequence and is ready for operation |
| shutdownInitiated          | Shutdown initiated, indicating that the robot has begun its shutdown sequence |
| modeChanged                | Mode changed, indicating that the robot has switched to a different operational mode,  see class operational_mode for possible values |
| faultRaised                | Fault raised, indicating that the robot has detected an error or issue in its systems |
| faultCleared               | Fault cleared, indicating that a previously raised fault or error condition in the robot's systems has been resolved |
| goalReached                | Goal reached, indicating that the robot has successfully reached its navigation goal |
| goalFailed                 | Goal failed, indicating that the robot was unable to reach its navigation goal |
| docked                     | Docked, indicating that the robot has successfully docked to a charging station |
| undocked                   | Undocked, indicating that the robot has successfully undocked from a charging station |
| object_detected            | Robot's sensors have detected an object in its environment, which may require navigation adjustments |
| pathBlocked                | Detected an obstruction or blockage in planned path, which may require re-planning |
| marker_detected            | Detected a specific marker or landmark, which may be used for localization, navigation, or interaction based on the nature of the detected marker |
| human_detected             | Detected the presence of a human which may require safety measures |
| manualOverride             | Manual override activated, indicating that a human operator has taken control of the robot's operations |
| remoteCommand              | Remote command received, indicating that the robot has received a command from a remote source |
| heartbeat                  | Robot has received expected heartbeat signal from a critical system or component within a specified time frame |
| configChanged              | Robot's configuration has been updated or modified, which may involve changes to its behavior |