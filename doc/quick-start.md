# Quick Start/Stop Scripts

Two shell script wrappers are provided for convenient starting and stopping of the oRover system.

## Scripts Location
Scripts are located in the `pi/` directory:
- `pi/start` - Starts the oRover system
- `pi/stop` - Gracefully stops the oRover system

## `start` Script
Launches the oRover system via the launcher process.

**Usage:**
```bash
cd pi/
./start              # Uses default config.ini
./start custom.ini   # Uses specified config file
```

**What it does:**
1. Changes to the script directory
2. Validates Python3 is available
3. Checks the config file exists
4. Launches `launcher.py` with the specified config

## `stop` Script
Sends a graceful shutdown command to the running oRover system.

**Usage:**
```bash
cd pi/
./stop              # Uses default config.ini
./stop custom.ini   # Uses specified config file
```

**What it does:**
1. Changes to the script directory
2. Validates Python3 is available
3. Checks the config file exists
4. Executes `stop.py` to publish shutdown command on event bus

## Example Workflow

```bash
cd /path/to/oRover/pi

# Start the system in the background
./start &

# Let it run...
# System is now active. Other processes can:
# - Connect to event bus
# - Send commands via event bus
# - Monitor logs in logs/ directory

# When ready to stop from another terminal:
./stop

# Or gracefully interrupt the foreground process:
# Press Ctrl+C - launcher handles SIGTERM
```

## Requirements

- Python 3.6+
- Bash shell
- Event bus available via config.ini `[eventbus]` parameters
- Config file accessible (default: `config.ini`)
- `launcher.py`, `stop.py`, and `eventbus.py` in pi directory

## Notes

- Both scripts are executable (chmod +x set)
- They validate that config files exist before attempting to launch
- They use relative paths and cd to script directory, so can be run from any directory
- `stop.py` requires a running event bus to send shutdown command
- `launcher.py` handles SIGTERM gracefully by stopping child processes in reverse order
- Logs are written to `logs/` directory with timestamps

## Related Documentation

- [launcher.md](launcher.md) - Process manager and system startup
- [stop.md](stop.md) - Shutdown helper script details
- [configuration.md](configuration.md) - Configuration file reference
- [eventbus.md](eventbus.md) - Event bus system overview
- [systemd.md](systemd.md) - System integration for auto-startup
