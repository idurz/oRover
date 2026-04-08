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

## Control path
Typical control flow:
1. Browser sends POST `/control` with an action (`forward`, `left`, `stop`, ...)
2. `app.py` maps action to wheel speeds
3. `app.py` publishes a bus event (`orover.cmd.set_motor_speed`)
4. Other components (for example `ugv.py`) consume and execute

## Config sections used
- `[app]` for Flask host/port/template/static settings
- `[eventbus]` and `[orover]` through shared `baseprocess` setup

See [configuration.md](configuration.md).
