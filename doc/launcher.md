# launcher

## Description
The launcher is the process manager for oRover. It reads `config.ini`, starts all
configured scripts, and handles graceful shutdown of child processes when a
termination signal is received.

By default, systemd sends `SIGTERM` when stop is requested (or during system
shutdown), then waits before sending `SIGKILL`. The launcher receives `SIGTERM`
and forwards `SIGTERM` to all started oRover processes.

## Command line parameters
- `--config`: Optional argument to specify the path to the configuration file. 
If not provided, it defaults to "config.ini" in the working directory.

## Parameters in config file

  * Parameters for the launcher should be in the section `[orover]`

|Parameter|Description|
|---------|-----------|
|python_exec=<X> |Python executable used to run oRover scripts. Defaults to `python3`|

Example:

```
[orover]
python_exec = python3
```

## How to start programs

The launcher starts all scripts and then waits for a termination signal. Scripts
to start are listed in the `[scripts]` section of the config file.

Each line describes one script. The format is `<name> = <script.py>`.
The name can be any descriptive string. If the script is in another directory,
use a relative or absolute path. Only Python scripts are supported.

Script parameters in the form `--param=value` can be added if the target script
supports them. By default, each started script receives
`--config=<launcher-config-file>`. Do not add that parameter manually in
`[scripts]`.

**Mandatory scripts are**
```
logserver.py
eventbus.py
boss.py
ugv.py
```

The `logserver.py` script should be listed first, as the other processes depend on it for logging.
For details on logserver configuration and log file management, see [logserver.md](logserver.md).

For convenient command-line startup and shutdown, see [quick-start.md](quick-start.md).

**Examples**
```
eventbus = eventbus.py
boss = boss.py
powercontrol = powercontrol.py
ugv = ugv.py
hcsr04 = hcsr04.py
webrover = app.py
```