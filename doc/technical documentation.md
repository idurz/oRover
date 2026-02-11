# oRover Technical Documentation 

## Summary

oRover is build on a distributed system where senors, actuars, motors and analyzers work together by sending messages via the [zeromq](https://zeromq.org/) request/reply format.
The [BOSS server](orovover.md) act as a controller and is the central heart of the oRover system. It runs in the background continous, accepts requests and status updates and makes decisions to control motors
and actuars based on that.

By using [zeromq](https://zeromq.org/) and a standarized message format between all elements the system is futureproof and easily adaptable for other type of sensors, image analyzers etc. Converting the message to specific hardware or software needs is done in separate modules which makes troubleshooting easier.

## Background
We decided to create oRover primarilry as a project to learn how such a robot should work. Learn about the hardware of such a system, about the software setup and how these two should work together. 

## Main components
The robot system is technical divided in two main components as described below

### ESP (Microcontroller)
- Motor control (tracks)
- Encoder reading
- Low-level safety logic
- Deterministic real-time behavior

The ESP Microcontroller is integral part of the [WaveShare UGV Tracked Robot](https://www.waveshare.com/wiki/UGV01) we used for the project. For now, we accept this chassis to work as is and we decided not to touch the ESP software running on that for now. More details on the ESP and the driver board can be found at the [driver board](doc/driverboard.md)

### Raspberry Pi
- AI vision processing
- Autonomous navigation logic
- Sensor fusion
- Mission planning
- User interface / remote control
- Data logging

There are some other projects running we had a look at. We also considered ROSS, the state of the art standard robot platform. For now, we decided to just start all over, because that is learning the hard way.

## Architecture guidelines

On the start of the project we decicded to note down a few guidelines and made some decisions based on that
- We will use Waveshare ESP drivers as is,leaving the software on the ESP untouched
- A host computer will act as control center where we can add intelligence 
- That host computer will be physically present on the robot and connect to the ESP with the provided serial interface
- Default tasks like driving and navigation must be possible without network connection
- Tasks are designed in such a way that additional service hosts can be added to offload tasks from the host computer
- ESP Driver communicates via serial port, therefore a host task to work with the ESP must run local
- Tasks need to be independant of each other and can run on the host or somewhere else
- Tasks must communicate via a distributed method, using [0MQ](https://zeromq.org/get-started/) as message bus, reasoning
  - allows for pub/sub event systems
  - allows for request/reply commands
  - ideal for distributed systems, does not need main server like MQTT
- Tasks are desigend as multiple processes, not threads because
  - A crash or memory leak in one script won’t kill everything
  - Much easier to restart, upgrade, debug, and monitor
  - You can easily move scripts to other machines later with no redesign
  - ØMQ is designed for inter-process communication, not threads

Based the above we decided to start our host controller work on a Raspberry PI, and decided on Python as the main programming language. Tasks are independant Python programs which work together by communicating via the [ZeroMQ](https://zeromq.org/get-started/) stack.

## The grand picture

The OS, via the job scheduler, will ensure that oRover is automatic started at system startup. Actually systemd wil start only the oRover launcher. The launcher reads the config, to verify which other parts of the system are present and will start these programs in the background. The 
- event bus, 
- ugv controller and
- oRover boss
should be started at the minimum. Other components e.g. for sensors etc. need to be started by the launcher as well. The oRover system consists of the following parts:

![system view](./pics/orover%20system%20view.png)

Follow the blue links in the table for the descriptions of the components:

|Owner |Component                        |Description                                                                    |
|------|---------------------------------|-------------------------------------------------------------------------------|
|os    |[systemd](systemd)               |OS level systemd scheduler which stops/starts launcher, outside of oRover      |
|oRover|[configuration](configuration)   |Summary of working and all items in the configuration file                     |
|oRover|[launcher](launcher)             |Anchor points which starts and stops other scripts of the system               |
|oRover|[ugv controller](ugv)            |Actor scripts which translates BOSS commands to serial UGV board commands      |
|oRover|[driver board](driverboard)      |The UGV system ESP microcontroller, sensors and motor actors                   |
|oRover|[event bus](eventbus)            |Event bus script which act as central message server                           |
|oRover|[enumeration](enumeration)       |Enumeration of commands, states events and other important message parts       |
|oRover|[robot controller](boss_server)  |BOSS of oRover which decides on actions based on events                        |
|option|[mqtt connector](mqtt)           |Optional MQTT connector script translating event buss messages to MQTT         |
|option|[web portal](web)                |Web portal for manual control of the oRover system                             |
|option|[powercontrol](power)            |Shutdown control program to enable delayed power down                          |
|user  |[service controller](controller) |One or more task controllers for e.g. vision, object recognition, path planning|
|user  |[other actor](actor)             |One or more specific actors, e.g. grippers, docking                            |
|user  |[sensor server](sensor)          |One or more sensor script, e.g. Lidar, ultrasonic, collision, temperature      |
---