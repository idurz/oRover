# oRover Quick Start/Stop

Two shell script wrappers are provided for convenient starting and stopping of the oRover system.

## Scripts

### `start`
Launches the oRover system via the launcher process.

**Usage:**
```bash
export PATH="$PWD/.venv/bin:$PATH"  # Run from pi/ after installation
./start              # Uses /etc/orover/config.ini
./start custom.ini   # Uses specified config file
```

**What it does:**
1. Changes to the script directory
2. Validates Python3 is available
3. Checks the config file exists
4. Launches `launcher.py` with the specified config

### `stop`
Sends a graceful shutdown command to the running oRover system.

**Usage:**
```bash
export PATH="$PWD/.venv/bin:$PATH"  # Run from pi/ after installation
./stop              # Uses /etc/orover/config.ini
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
export PATH="$PWD/.venv/bin:$PATH"

# Start the system in the background
./start

# Let it run...
# When ready to stop:
./stop

# Or stop from another terminal while system is running
./stop
```

## Requirements

- Python 3 and the project dependencies (installed in `pi/.venv` by the installer)
- Event bus running (started by launcher)
- Launcher and stop.py processes in the pi directory
- Config file accessible (default: `/etc/orover/config.ini`)

## Notes

- Both scripts are executable (chmod +x already set)
- They validate that config files exist before attempting to launch
- They change to the script directory; relative configuration paths are resolved there
- `stop.py` requires a running event bus to send shutdown command
- `launcher.py` handles the shutdown gracefully by stopping child processes
- Web UI telemetry rendering now tolerates non-numeric IMU/battery payload fields; invalid values display as `--` instead of causing browser `toFixed` runtime errors.

## See Also

- [launcher.md](../doc/launcher.md) - Process manager documentation
- [stop.md](../doc/stop.md) - Shutdown helper documentation
- [configuration.md](../doc/configuration.md) - Configuration file structure
