# Configuration of the system

## background
The launcher takes care of starting all other components. For that it needs to know which scripts are available in the system. It reads a configuration file and decides on actions. The configuration file is a text-readable file with sections it. Each section contains parameters for parts of the system.

## example
A configuration file looks like this:

```
[event]
type = campfire
place = outdoor

[time]
saturday = 19:00-21:00
```

The configuration example above could describe the type of event which will happen on saturday's between 19:00-21:00.

## location
If no parameter is given the launcher expects a `config.ini` file in its working directory. If you decide to use another file, use the `--config=<anotherfile.ini>` parameter, more info on the (launcher)[launcher.md] section.

## how to
This same configuration file as used by the launcher is passed as parameter to all other script. Each script should handle reading that file and gettings is parameter from there. Use the python libraries (configparser)[https://docs.python.org/3/library/configparser.html] and (argparse)[https://docs.python.org/3/library/argparse.html] for that.

Default code as shown below could help you forward:

```
import configparser
import argparse

# Check if config file is given as argument, otherwise use default
parser = argparse.ArgumentParser(description="oRover startup script"
                                ,prog="python3 launcher.py")
parser.add_argument("--config",type=str,required=False,default="config.ini"
                   ,help="Path to configuration file (default: config.ini)")
                   
args = parser.parse_args()

# Read configuration from config.ini file
config = None   
if not os.path.isfile(args.config):
    sys.exit(f"Configuration file {args.config} does not exist")

config = configparser.ConfigParser() 
config.read(args.config)

# Using example parameter from above
next_event_type = config.get("event","type",fallback="nothing planned")
print(f"Please go to {next_event_type}")
```

## Items in configuration file

**All lines have the format `<name> = <content>`**

### Section [orover]
| name              | default value    | description |
|-------------------|------------------|-------------|
| python_executable | python3          | Location/path of used python program |
| logfile           | orover.log       | path/name used by oRovers FileHandler for storing system messages |
| subscribe_socket  | tcp://localhost:5555 | ZMQ bind address the event bus subscribe listener |
| publish_socket    | tcp://*:5555     |  ZMQ bind address the event bus publish sends to      |

### Section [app]
| name              | default value    | description |
|-------------------|------------------|-------------|
| name              | orover           | Flask app name used when constructing the (Flask)[https://flask.palletsprojects.com/en/stable/] web app |
| static_folder     | ./static         | override Flask's static (e.g. pictures etc) directories |
| template_folder   | ./template       | override Flask's template (e.g. html, js) directories |
| debug             | False            | boolean for Flask debug mode |

### Section [processes]
| name              | default value    | description |
|-------------------|------------------|-------------|
| 'acronym'         | 'none'           | filename of a python script which should be started by the launcher. path/filename should end in `py`

Example `boss = boss.py`

### Section [ugv]
| name              | default value    | description |
|-------------------|------------------|-------------|
| port              | /dev/serial0     | serial port used for communication between ugv script and (driverboard)[driverboard.md] |
| baudrate          | 115200           | baudrate used for serial communication between ugv script and (driverboard)[driverboard.md] |

### Section [powercontrol]
| name              | default value    | description |
|-------------------|------------------|-------------|
| pin               | 4                | Pin number where the powercontrol detection is connected. See (power)[power.md] |
| sleep_time        | 2.0              | Seconds to wait after the signal pin dropped to avoid glitches in the system |

### Section [hcsr04]
| name              | default value    | description |
|-------------------|------------------|-------------|
| sensor'x'         | 'none'           | comma-separated triple `name, triggerpin, echopin` used to enumerate sensors and GPIO pins |
| object_notify_distance | 20          | distance threshold (cm) to trigger an `object_detected` event |

Sensor numbers should start with 1 and numbered in sequence. The sensor name used should be known to the system in the (enumeration)[enumeration.md]. Pin numbers used for the hardware connection are in BCM format.

Example `sensor1 = sensor_ultrasonic_front, 17, 27`