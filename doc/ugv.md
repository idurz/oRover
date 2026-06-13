# UGV interface

## Goal
`pi/ugv.py` bridges bus commands to ESP32 serial commands and forwards ESP32
feedback back to the event bus.

## Runtime model
The process is a `baseprocess` client with a custom main loop:
- polls ZMQ SUB for bus messages
- reads serial data from the ESP32 (`read(1024)`)
- parses serial data line-by-line (newline framed)

## Incoming and outgoing bus connections

### Incoming (handled in `ugv.py`)
- `cmd.move` via `cmd_move(message)`
- `cmd.moveTo` via `cmd_moveTo(message)`
- `cmd.moveRoute` via `cmd_moveRoute(message)`
- `cmd.getParam` via `cmd_getParam(message)`
- `cmd.setParam` via `cmd_setParam(message)`
- `cmd.set_motor_speed` via `cmd_set_motor_speed(message)`
- `event.obstacleDetected` via `event_obstacleDetected(message)`

### Outgoing (published in `ugv.py`)
- `state.battery` from typed serial feedback `T=1001`
- `state.motion` from typed serial feedback `T=1001` and `T=1002`
- `state.sensor_status` from typed serial feedback `T=1003`, `T=1004`, `T=1005`
    and from untyped JSON forwarding
- `state.pose` from typed serial feedback `T=1051`
- `state.actuator_speed` from typed serial feedback `T=139`

### Outgoing inherited from `baseprocess`
- `event.heartbeat` is published periodically by `_heartbeat_loop` when
    `heartbeat_interval > 0` in config.

`ugv.py` uses its own handler class, so base handler commands (`cmd.stop`,
`cmd.pause`, `cmd.resume`) are not auto-registered here.

## Command handlers currently implemented
The handler class currently exposes these command entry points:
- `cmd_move(message)`
- `cmd_moveTo(message)`
- `cmd_moveRoute(message)`
- `cmd_getParam(message)`
- `cmd_setParam(message)`
- `cmd_set_motor_speed(message)`
- `event_obstacleDetected(message)`

The most used command path is motor control:
- incoming bus command `cmd.set_motor_speed`
- serialized to ESP32 JSON `{"T":1,"L":<left>,"R":<right>}`
- written to serial with trailing newline

Route/motion behavior:
- `cmd_move` creates a one-step route with explicit wheel speeds and no end condition
- `cmd_moveTo` creates a one-step route with `distance` and `angle`
- `cmd_moveRoute` validates and executes `body.route` sequentially
- route execution runs in a worker thread (`move_rover_thread`) and processes each segment through `_move_segment`
- `cmd_set_motor_speed` updates default linear/angular speeds used for later movement helpers

## Serial receive format
ESP32 serial output is handled as newline-delimited frames.

For each line, `ugv.py` classifies input as:
- typed JSON: object with integer `T`
- untyped JSON: object without `T`
- plain text: non-JSON lines (logged only)

## Typed serial messages wired to the bus
The following typed messages are mapped from ESP32 serial input:

- `T=1001` base feedback
    - publishes `state.battery` with `{"voltage": v}`
    - publishes `state.motion` with heading/roll/pitch and wheel speeds
- `T=1002` IMU feedback
    - publishes `state.motion` with IMU channels (`ax/ay/az`, `gx/gy/gz`, `mx/my/mz`)
- `T=1003` ESP-NOW receive
    - publishes `state.sensor_status` (`channel=esp_now_recv`)
- `T=1004` ESP-NOW send status
    - publishes `state.sensor_status` (`channel=esp_now_send`)
- `T=1005` servo bus status
    - publishes `state.sensor_status` (`channel=servo_bus`)
- `T=1051` RoArm feedback
    - publishes `state.pose` with arm pose/torque fields
- `T=139` speed-rate feedback
    - publishes `state.actuator_speed` with left/right rate

## Untyped JSON messages wired to the bus
Untyped JSON lines are also forwarded as `state.sensor_status`:
- `channel=wifi_status` for payloads with keys like `ip`, `rssi`, `wifi_mode_on_boot`
- `channel=system_status` for payloads with keys like `info`, `mac`, `status`
- `channel=serial_json_untyped` fallback for other JSON payloads

Each forwarded event includes:
- `src = orover.origin.orover_ugv`
- `reason = orover.state.sensor_status`
- `body = {"channel": <channel>, "payload": <original-json>}`

## Notes
- The code currently contains additional movement helper functions that are still
    under active development. The serial bridge and feedback routing described
    above reflect the currently wired behavior.

See also:
- [commandset.md](commandset.md)
- [boss_server.md](boss_server.md)
- [app.md](app.md)
