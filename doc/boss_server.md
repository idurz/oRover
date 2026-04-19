# BOSS server

## Goal
`boss.py` is the central monitoring process on the oRover event bus. It listens
for events and state messages, validates message structure via `baseprocess`, and
runs handler routines for known topics.

## Runtime model
BOSS does not use a request/reply socket API. It is a long-running subscriber
process built on `baseprocess`.

At startup it:
- reads config and logging settings
- creates PUB/SUB sockets through `baseprocess`
- discovers handlers from method names
- enters the main receive loop (`run()`)

## Handler registration
Handlers are auto-registered by naming convention in the handler class:
- `event_<name>(msg)`
- `cmd_<name>(msg)`
- `state_<name>(msg)`

`baseprocess.fetchtopics()` scans these methods and maps them to the proper
enum reason values. This is how dispatch is built in the current codebase.

## Message validation
Incoming messages are validated before dispatch. The validation includes:
- required fields present
- valid UUID in `id`
- valid timestamp in `ts`
- valid source (`src`) enum value
- valid priority (`prio`) enum value

Messages that fail validation are discarded and logged.

## Current BOSS handlers
Typical handlers in `boss.py` are:
- `event_heartbeat(msg)`: stores heartbeat timestamps per process
- `event_object_detected(msg)`: validates obstacle distances and updates the local grid map
- `state_motion(msg)`: stores heading/pitch/roll and left/right speed, then updates pose integration
- `state_battery(msg)`: stores latest battery voltage in navigation state

## Background loops
In addition to message handlers, `boss.py` starts optional daemon loops (config-driven):
- `snapshot_logger_loop`: periodic debug snapshot logging
- `publish_pose_loop`: publishes aggregated navigation snapshots as `state.pose`

Published pose snapshot body includes:
- pose (`x_m`, `y_m`, `heading_deg`)
- speed (`left_mps`, `right_mps`)
- battery voltage
- obstacle count
- occupancy grid preview

## Configuration
BOSS is started by `launcher.py` via the `[scripts]` section in `config.ini`.
Bus endpoints and log behavior come from shared config sections:
- `[eventbus]`
- `[orover]`

See [configuration.md](configuration.md) and [eventbus.md](eventbus.md).
