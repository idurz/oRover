# app (web server)

## Goal
`app.py` provides the web interface for oRover. It exposes HTTP endpoints and
Socket.IO events, and bridges browser actions to eventbus commands.

## Runtime behavior
The process starts as a `baseprocess` client with threaded ZMQ listening enabled.
This allows Flask request handling and eventbus message handling to run together.

## Message handlers
`app.py` registers handlers using the same naming convention as other bus
clients:
- `event_heartbeat(msg)`: updates heartbeat state and emits websocket updates
- `state_battery(msg)`: emits battery voltage updates
- `state_imu(msg)`: emits IMU updates
- `state_pose(msg)`: accepts navigation snapshots from `orover_boss` and emits `nav_state`

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
