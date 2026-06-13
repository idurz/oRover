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

## Recent updates

### 2026-06-04: Web telemetry rendering hardening

- Browser telemetry rendering now safely normalizes IMU (`heading`, `pitch`, `roll`) and battery (`voltage`) values before numeric formatting.
- This prevents client-side failures such as `TypeError: data.roll.toFixed is not a function` when upstream payloads contain strings, null values, or missing fields.
- Invalid or non-numeric values are rendered as `--` so real-time updates continue without breaking the UI.

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

## Bus connection overview

The process-level docs now include explicit incoming and outgoing bus
connections. A key implementation detail is shared inheritance from
`baseprocess`:

- Most long-running bus clients (`boss.py`, `ugv.py`, `app.py`, `launcher.py`)
  inherit publishing via `send_event()` and can publish `event.heartbeat` via
  `_heartbeat_loop` when `heartbeat_interval > 0`.
- Actual incoming handlers are defined by each process-specific handler class
  and auto-registered by naming convention (`event_*`, `cmd_*`, `state_*`).
- When a process defines its own handler class, base handler methods
  (`cmd.stop`, `cmd.pause`, `cmd.resume`) are not automatically included unless
  explicitly composed/inherited by that handler.

For explicit in/out lists per component, see:
- [boss_server.md](boss_server.md)
- [ugv.md](ugv.md)
- [app.md](app.md)
- [launcher.md](launcher.md)
- [stop.md](stop.md)

### Process connection matrix

| Process | Incoming (handled) | Outgoing (explicit in process) | Outgoing (inherited from `baseprocess`) |
|---|---|---|---|
| `boss.py` | `event.heartbeat`, `event.object_detected`, `state.motion`, `state.battery` | `cmd.shutdown` (battery critical), `event.lowBattery` (battery low) | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `ugv.py` | `cmd.move`, `cmd.moveTo`, `cmd.moveRoute`, `cmd.getParam`, `cmd.setParam`, `cmd.set_motor_speed`, `event.obstacleDetected` | `state.battery`, `state.motion`, `state.sensor_status`, `state.pose`, `state.actuator_speed` | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `app.py` | `event.heartbeat`, `state.battery`, `state.motion`, `state.pose` | `cmd.moveRoute`, `cmd.set_motor_speed` | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `launcher.py` | `cmd.shutdown` | none (process orchestration only) | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `stop.py` | none (one-shot publisher) | `cmd.shutdown` | possible but not relied on: `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `hcsr04.py` | none (sensor publisher) | `event.object_detected` | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `cmdline.py` | none (interactive publisher) | user-selected `cmd.*` | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |
| `test/testcmd.py` | none (interactive test publisher) | user-selected `cmd.*` | `event.heartbeat` via `_heartbeat_loop` when `heartbeat_interval > 0` |

Notes:
- `eventbus.py` is a ZeroMQ proxy process and does not register `event_*`, `cmd_*`, `state_*` handlers as bus topics.
- `logserver.py` and `powercontrol.py` are not eventbus topic handlers/publishers in the same way as bus client processes above.

## Reusable bus tests

The `pi/test/` directory now includes reusable integration test programs that
exercise bus traffic and verify observable outcomes:

- `boss_test.py` publishes `state.battery` and expects `event.lowBattery`
- `ugv_test.py` publishes `cmd.set_motor_speed` and expects a matching UGV feedback topic
- `app_test.py` calls `POST /control` and expects `cmd.set_motor_speed` on the bus
- `stop_test.py` runs `stop.py` and expects `cmd.shutdown` from `orover_stopper`
- `launcher_test.py` runs `launcher.py` with a temporary config and expects shutdown handling

The shared helper library is `pi/test/bus_testlib.py`. It handles:
- config loading
- PUB/SUB setup
- slow-joiner mitigation
- message construction in the same format as `baseprocess.send_event()`
- reusable expectation checks for different process scenarios

See [pi/test/README_bus_tests.md](../pi/test/README_bus_tests.md) for run
examples and scenario details.

---