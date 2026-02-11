# launcher

## Description
The launcher is a core Python script from oRover. The purpose is initializing and starting all configured processes 
for the oRover project. It reads the configuration from a specified config file (defaulting to "config.ini"), 
starts each process defined in the configuration, and handles graceful shutdown of itself and all child processes 
when a termination signal is received. The launcher ensures that all processes are started with the 
correct Python executable as specified in the configuration.

By default, a SIGTERM is sent by systemd when a stop is requested (or a system shutdown), followed by 90 seconds of waiting followed by a SIGKILL. Launcher receives the SIGTERM and starts sending SIGTERM signals to its known processes in the oRover system.

## Command line parameters
- `--config`: Optional argument to specify the path to the configuration file. 
If not provided, it defaults to "config.ini" in the working directory.

## Parameters in config file

  * Parameters for the launcher should be in the section `[orover]`

|Parameter|Description|
|---------|-----------|
|python_executable=<X> |Python path for running the oRover scripts. Defaults to `python3`|

## How to start programs

The launcher starts all the scripts and waits for a termination signal. The scripts which needs to be started are described in the `[scripts]` section of the config file.

Each line in the config file describes one script. The format of the line is `<name> = <script.py>`
The name kan be any string, a representative name is suggested. If the script resides in another directory, use the path to it.You can only start python scripts. 

Script parameters in the vorm `--param=myparam` can be added if your script handles them. By default each script gets the parameter `--config=config.ini` as a copy of the ini file which is used for this launcher script. That parameter should not be added in the processes section.

**Mandatory scripts are**
```
eventbus.py
boss.py
ugv.py
```

**Examples**
```
eventbus = eventbus.py
boss = boss.py
powercontrol = powercontrol.py
ugv = ugv.py
hcsr04 = hcsr04.py
web = app.py
```