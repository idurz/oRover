# app (web server)

## Goal
`app.py` provides the web interface for oRover. It exposes HTTP endpoints and
Socket.IO events, and bridges browser actions to eventbus commands.

## Runtime behavior
The process starts as a `baseprocess` client with threaded ZMQ listening enabled.
This allows Flask request handling and eventbus message handling to run together.

## Incoming and outgoing bus connections

### Incoming (handled in `app.py`)
- `event.heartbeat` via `event_heartbeat(msg)`
- `state.battery` via `state_battery(msg)`
- `state.motion` via `state_motion(msg)`
- `state.pose` via `state_pose(msg)`

### Outgoing (published in `app.py`)
- `cmd.moveRoute` from route-loading flow (`rx_commands`)
- `cmd.set_motor_speed` from `POST /control`

### Outgoing inherited from `baseprocess`
- `event.heartbeat` is published periodically by `_heartbeat_loop` when
	`heartbeat_interval > 0` in config.

`app.py` uses its own handler class, so base handler commands (`cmd.stop`,
`cmd.pause`, `cmd.resume`) are not auto-registered here.

## Message handlers
`app.py` registers handlers using the same naming convention as other bus
clients:
- `event_heartbeat(msg)`: emits Socket.IO `heartbeat` event `{me, ts}`
- `state_battery(msg)`: emits Socket.IO `battery` event `{voltage}`
- `state_motion(msg)`: emits Socket.IO `imu` event `{h, p, r}`
- `state_pose(msg)`: validates and emits Socket.IO `pose` event (see below)

## Pose handling
`state_pose` reads the canonical nested payload from `boss.py`:
```
body.pose.x_m
body.pose.y_m
body.pose.heading_deg
body.grid.preview   (optional 2-D list)
body.ts             (optional timestamp)
```
For backward compatibility, flat top-level `body.x_m / body.y_m / body.heading_deg` is also accepted.
All three coordinate fields must be numeric; malformed payloads are discarded with a warning log.

The Socket.IO `pose` event emitted to browsers:
```json
{ "x": 0.0, "y": 0.0, "h": 0.0, "ts": "...", "grid": { "preview": [[...]] } }
```
The `grid` field is only present when a valid 2-D preview list was received.

## Emitting states to browser
Each handler emits a Socket.IO event directly when a bus message arrives.
There is no periodic batch-emit thread; updates reach the browser as events occur.

Web UI note (2026-06-04):
- The browser-side Socket.IO handlers in `pi/template/index.html` now normalize IMU and battery values before numeric formatting.
- This prevents failures like `TypeError: data.roll.toFixed is not a function` when incoming payload values are strings, null, or missing.
- Invalid values display as `--` instead of interrupting real-time UI updates.

## Control path
Typical control flow:
1. Browser sends POST `/control` with an action (`forward`, `left`, `stop`, ...)
2. `app.py` maps action to wheel speeds
3. `app.py` publishes a bus event (`orover.cmd.set_motor_speed`)
4. Other components (for example `ugv.py`) consume and execute

Route flow:
1. Browser sends POST `/route` with a JSON list in `route`
2. `app.py` stores that route in `commands.csv`
3. `app.py` reads `commands.csv`, builds a payload `{id, route:[{distance, angle}, ...]}`
4. `app.py` publishes `orover.cmd.moveRoute` with that payload in `body`

## HTTP routes currently exposed
- `GET /` renders the main UI
- `POST /publish` publishes a generic bus message
- `GET /messages` returns recent in-memory messages
- `POST /control` sends wheel speed commands
- `POST /readroute` loads `commands.csv` and sends one `cmd.moveRoute` command
- `POST /route` validates route JSON, stores it to `commands.csv`, then triggers `cmd.moveRoute`

## Config sections used
- `[app]` for Flask host/port/template/static settings
- `[eventbus]` and `[orover]` through shared `baseprocess` setup

See [configuration.md](configuration.md).
