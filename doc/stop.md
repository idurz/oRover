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

## How to run
From the `pi` directory:

```bash
python3 stop.py --config=config.ini
```

Alternatively, use the convenient `stop` shell script:

```bash
./stop config.ini
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
