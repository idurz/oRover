# Configuration of the system

## Background
`launcher.py` starts oRover components based on a shared INI configuration file.
By default this file is `config.ini` in the working directory.

You can override the file path with:

```
--config=<path-to-config.ini>
```

See [launcher.md](launcher.md).

## Reading config in scripts
Every process should accept `--config` and read values from that file.
Python standard libraries to use:
- [configparser](https://docs.python.org/3/library/configparser.html)
- [argparse](https://docs.python.org/3/library/argparse.html)

## Format
Each section contains key/value pairs in the form:

```
name = value
```

## Sections used by oRover

### Section [orover]
| name | default | description |
|---|---|---|
| python_exec | python3 | Python executable used by launcher |
| heartbeat_interval | 10 | Interval (seconds) between heartbeat messages; `0` disables heartbeat |
| loglevel | DEBUG | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| logdir | logs | Directory where log files are stored |
| logfile | orover.log | Log file basename (timestamp appended automatically) |
| max_logfiles | 10 | Maximum number of log files to retain; older files are automatically deleted |
| logformat | %(asctime)s %(name)-8s %(levelname)-9s guid=%(guid)s %(message)s | Log format string; includes guid for message tracing |
| logdatefmt | %Y-%m-%d %H:%M:%S | Date format used in logs |

### Section [app]
| name | default | description |
|---|---|---|
| static_folder | static | Flask static folder |
| template_folder | template | Flask template folder |
| debug | True | Flask debug mode |
| host | 0.0.0.0 | Flask bind address |
| port | 5000 | Flask bind port |
| secret_key | (set in config) | Flask secret key |

### Section [scripts]
Defines scripts started by launcher.

Example:

```
[scripts]
logger = logserver.py
eventbus = eventbus.py
boss = boss.py
ugv = ugv.py
webrover = app.py
```

### Section [eventbus]
| name | default | description |
|---|---|---|
| client_pub_socket | tcp://localhost:5556 | Endpoint where bus clients publish |
| client_sub_socket | tcp://localhost:5555 | Endpoint where bus clients subscribe |
| bus_xsub_socket | tcp://localhost:5556 | Eventbus XSUB connect target |
| bus_xpub_socket | tcp://*:5555 | Eventbus XPUB bind target |
| capture_message_ids | False | If enabled, eventbus logs message ids passing through proxy |

See [eventbus.md](eventbus.md).

### Section [serial]
| name | default | description |
|---|---|---|
| port | /dev/serial0 | Serial device used by `ugv.py` |
| baudrate | 115200 | Serial speed |
| timeout  | 0.1    | Serial read timeout in seconds |

### Section [powercontrol]
| name | default | description |
|---|---|---|
| pin | 4 | GPIO pin (BCM numbering) for power-loss detect |
| sleep_time | 2.0 | Debounce wait (seconds) after signal drop |

See [power.md](power.md).

### Section [hcsr04]
| name | default | description |
|---|---|---|
| sensor1..sensorN | none | `name, triggerpin, echopin` sensor definition |
| min_obj_distance | 20.0 | Distance threshold (cm) for object-detected event. Set this value to 0 to receive all
messages regardless of distance |
| polling_interval | 0.5 | Poll interval per sensor (seconds) |
| echo_timeout | n/a (fixed 0.04 in code) | Config key present in `config.ini`, currently not consumed by `hcsr04.py` |
| speed_of_sound | n/a (fixed 34300.0 in code) | Config key present in `config.ini`, currently not consumed by `hcsr04.py` |

### Section [ugv]
| name | default | description |
|---|---|---|
| linear_speed | 0.5 | Movement helper linear speed (m/s) |
| angular_speed | 90.0 | Movement helper angular speed (deg/s) |
| cmd_period | 0.1 | Command resend period (seconds) |

### Section [boss]
| name | default | description |
|---|---|---|
| snapshot_log_interval | 5.0 | Periodic navigation snapshot debug logging interval (seconds), `0` disables |
| pose_publish_interval | 0.5 | Pose/state publish interval (seconds), `0` disables |
| grid_size | 81 | Occupancy grid width/height in cells |
| grid_resolution_m | 0.10 | Grid resolution in meters per cell |
| grid_preview_size | 21 | Preview crop size used in published snapshots |
| max_obstacle_range_m | 3.5 | Maximum obstacle range inserted into the grid |

### Section [lister]
| name | default | description |
|---|---|---|
| ignore_heartbeat | True | `listner.py` option to hide heartbeat topics |

Sensor pins use BCM numbering. Sensor names should match known values from
[enumeration.md](enumeration.md).
