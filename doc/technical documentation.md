# oRover Technical Documentation 

## Summary

oRover is built as a distributed system where sensors, actuators, motors and
analyzers communicate through a [ZeroMQ](https://zeromq.org/) pub/sub event
bus.

The [BOSS server](boss_server.md) is the central controller in this setup. It
runs continuously, consumes events and state updates, maintains navigation
state, and publishes aggregated pose snapshots for downstream consumers.

By using [ZeroMQ](https://zeromq.org/) and a standardized message format, the
system is modular and adaptable for additional sensors and services. Protocol
translation to specific hardware/software happens in dedicated modules, which
makes troubleshooting easier.

## Background
We decided to create oRover primarilry as a project to learn how such a robot should work. Learn about the hardware of such a system, about the software setup and how these two should work together. 

## Main components
The robot system is technical divided in two main components as described below

### ESP (Microcontroller)
- Motor control (tracks)
- Encoder reading
- Low-level safety logic
- Deterministic real-time behavior

The ESP microcontroller is an integral part of the
[WaveShare UGV Tracked Robot](https://www.waveshare.com/wiki/UGV01). More
details on the ESP and the driver board are in
[driverboard.md](driverboard.md).

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
  - supports request/reply patterns when needed
  - ideal for distributed systems, does not need a central broker process like MQTT
- Tasks are desigend as multiple processes, not threads because
  - A crash or memory leak in one script won’t kill everything
  - Much easier to restart, upgrade, debug, and monitor
  - You can easily move scripts to other machines later with no redesign
  - ØMQ is designed for inter-process communication, not threads

Based the above we decided to start our host controller work on a Raspberry PI, and decided on Python as the main programming language. Tasks are independant Python programs which work together by communicating via the [ZeroMQ](https://zeromq.org/get-started/) stack.

## The grand picture

The OS, via the job scheduler, can ensure oRover is automatically started at
system startup. In practice, `systemd` starts only the oRover launcher. The
launcher reads the config, determines which components are enabled, and starts
these processes in order. The
- event bus, 
- ugv controller and
- oRover boss
should be started at the minimum. Other components e.g. for sensors etc. need to be started by the launcher as well. The oRover system consists of the following parts:

![system view](./pics/orover%20messaging-system%20view.drawio.png)

Follow the blue links in the table for the descriptions of the components:

|Owner |Component                        |Description                                                                    |
|------|---------------------------------|-------------------------------------------------------------------------------|
|os    |[systemd](systemd.md)               |OS-level scheduler that starts/stops launcher outside of oRover             |
|oRover|[configuration](configuration.md)   |Configuration reference for active and optional sections                      |
|oRover|[launcher](launcher.md)             |Process manager that starts/stops configured scripts                          |
|oRover|[quick-start](quick-start.md)       |Shell wrappers for convenient startup and shutdown                            |
|oRover|[ugv controller](ugv.md)            |Bridge that translates bus commands to ESP serial and maps serial feedback    |
|oRover|[driver board](driverboard.md)      |UGV ESP microcontroller, sensors, and motor interfaces                        |
|oRover|[event bus](eventbus.md)            |ZeroMQ XSUB/XPUB proxy for topic-based communication                          |
|oRover|[enumeration](enumeration.md)       |Commands, states, events, and other enum definitions                          |
|oRover|[robot controller](boss_server.md)  |Central state controller and pose/grid publisher                              |
|oRover|[web portal](app.md)                |Flask/Socket.IO interface for monitoring and manual control                   |
|oRover|[stop helper](stop.md)              |One-shot script publishing shutdown command                                   |
|oRover|[enum uniqueness test](test_enum_name_uniqueness.md) |Regression test for duplicate enum member names                |
|option|[powercontrol](power.md)            |Power-loss watchdog / delayed power-down helper                              |
|option|future connectors                   |Optional integrations such as MQTT or external service bridges               |

## Logging Architecture

oRover uses a centralized socket-based logging system where all processes send log records to a central `logserver.py` that writes them to disk.

### Structured Logging with GUID Correlation

Starting from 2026-04-11, all log records include a `guid` field for message tracing:

- **Each bus message** gets a unique UUID (`id` field) assigned when created by `send_event()` in [base_process.py](../pi/base_process.py)
- **All log records** associated with that message carry the same `guid` value, allowing complete end-to-end tracing across processes
- Log context is propagated automatically using Python's `contextvars`, so handlers can log related activity with the same guid
- When a message is received via `handle_message()`, the incoming message guid becomes the logging context, ensuring all processing steps are grouped
- Logs without an associated message show `guid=-` (null guid)

Example log output:
```
2026-04-11 14:23:45 boss       INFO     guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Handling motion command
2026-04-11 14:23:45 ugv        DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Setting motor speed to 50
2026-04-11 14:23:46 boss       DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Motion complete
```

This enables:
- Rapid correlation of events across multiple processes during a single command flow
- Debugging of asynchronous behavior without manually parsing log files
- Better log filtering and analysis tools in the future

### Log File Organization

Log files are stored in a `logs/` directory (configurable via `logdir` in config.ini) with automatic rotation:

- Each startup creates a new timestamped log file: `orover_YYYYMMDDHHMMSS.log`
- The system automatically retains only the last N log files (default 10, configurable via `max_logfiles`)
- Old log files are deleted to prevent unbounded disk usage
- See [configuration.md](configuration.md) for details on `logdir` and `max_logfiles` parameters

---