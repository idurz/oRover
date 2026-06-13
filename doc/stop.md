# stop

## Goal
`stop.py` is a one-shot helper script that publishes a shutdown command on the
oRover event bus.

It is intended for manual shutdown requests from the command line.

## What it does
When executed, the script:
- creates a `baseprocess` instance to get config, logger, and bus sockets
- prints a local message that a stop was requested
- publishes a bus event with:
  - `reason = orover.cmd.shutdown`
  - `body = {"value": "requested by stop.py"}`

The receiving process (typically `launcher.py`) is expected to handle this
shutdown command and stop child processes gracefully.

## Incoming and outgoing bus connections

### Incoming (handled in `stop.py`)
- none (one-shot publisher)

### Outgoing (published in `stop.py`)
- `cmd.shutdown` with `body = {"value": "requested by stop.py"}`

### Outgoing inherited from `baseprocess`
- `event.heartbeat` can be published by `_heartbeat_loop` when
  `heartbeat_interval > 0` in config, but `stop.py` is intended as a short-lived
  helper and should not rely on heartbeat traffic.

## How to run
From the `pi` directory:

```bash
python3 stop.py --config=config/config.ini
```

Alternatively, use the convenient `stop` shell script:

```bash
./stop config/config.ini
```

See [quick-start.md](quick-start.md) for more details on the shell script wrappers.

## Dependencies
- shared config loading through `oroverlib.readConfig()`
- event bus connectivity via section `[eventbus]` in `config.ini`
- a running event bus process (`eventbus.py`)
- a receiver that handles `cmd.shutdown` (for example `launcher.py`)

## Related docs
- [eventbus.md](eventbus.md)
- [launcher.md](launcher.md)
- [configuration.md](configuration.md)
- [enumeration.md](enumeration.md)
