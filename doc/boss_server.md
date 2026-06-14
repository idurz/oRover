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

## Incoming and outgoing bus connections

### Incoming (handled in `boss.py`)
- `event.heartbeat` via `event_heartbeat(msg)`
- `event.object_detected` via `event_object_detected(msg)`
- `state.motion` via `state_motion(msg)`
- `state.battery` via `state_battery(msg)`

### Outgoing (published in `boss.py`)
- `cmd.shutdown` when battery is at or below shutdown threshold
- `event.lowBattery` when battery is below low threshold

### Outgoing inherited from `baseprocess`
- `event.heartbeat` is published periodically by `_heartbeat_loop` when
	`heartbeat_interval > 0` in config.

`boss.py` uses its own handler class, so base handler commands (`cmd.stop`,
`cmd.pause`, `cmd.resume`) are not auto-registered here.

## Message validation
Incoming messages are validated before dispatch. The validation includes:
- required fields present
- valid UUID in `id`
- valid timestamp in `ts`
- valid source (`src`) enum value
- valid priority (`prio`) enum value

Messages that fail validation are discarded and logged.

## Current BOSS handlers
- `event_heartbeat(msg)`: stores heartbeat timestamps per process
- `event_object_detected(msg)`: validates obstacle distances and updates the local occupancy grid
- `state_motion(msg)`: extracts heading, pitch, roll, left/right speed; calls `update_pose_from_motion`
- `state_battery(msg)`: triggers `event.lowBattery` or `cmd.shutdown` based on configured voltage thresholds

## Dead-reckoning pose integration
`update_pose_from_motion(heading, left_speed, right_speed)` is called on every `state.motion` message:
- integrates forward velocity `v = (left + right) / 2` over elapsed time `dt`
- updates `nav_state.pose.x_m` and `y_m` from heading and velocity
- overwrites `heading_deg` from IMU heading when present

## Background loops
In addition to message handlers, `boss.py` starts optional daemon loops (config-driven):
- `snapshot_logger_loop`: periodic debug snapshot logging
- `publish_pose_loop`: publishes `state.pose` snapshots at configured interval

Published `state.pose` body (canonical schema):
```
body.pose.x_m          float — robot x position in metres
body.pose.y_m          float — robot y position in metres
body.pose.heading_deg  float — robot heading in degrees
body.speed.left_mps    float — left wheel speed
body.speed.right_mps   float — right wheel speed
body.obstacle_count    int
body.grid.preview      2-D list of occupancy values
body.ts                ISO timestamp of last motion update
```

## Configuration
BOSS is started by `launcher.py` via the `[scripts]` section in `config.ini`.
Bus endpoints and log behavior come from shared config sections:
- `[eventbus]`
- `[orover]`

See [configuration.md](configuration.md) and [eventbus.md](eventbus.md).
