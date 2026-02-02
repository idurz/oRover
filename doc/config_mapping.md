| File | Section:Item(s) | Explanation |
|---|---|---|
| boss.py   | boss:logfile      | path/name used by the server's FileHandler (default `orover.log`)|
|           | boss:send_timeout | ZMQ send timeout (ms) applied via `context.setsockopt(zmq.SNDTIMEO)`|
|           | boss:boss_socket  | ZMQ bind address the BOSS `REP` socket listens on (default `tcp://*:5555`). |
| hcsr04.py | hcsr04:sensor1..sensorN | `sensorN` (e.g. `sensor1`): comma-separated triple `name, triggerpin, echopin` used to enumerate sensors and GPIO pins (validated and parsed by `getsensorinfo()`).|
|           | hcsr04.object_notify_distance` | distance threshold (cm) to trigger an `object_detected` event to BOSS. |
| TestRadar/app.py| app:name| Flask app name used when constructing the `Flask(...)` app.|
|                 | app:static_folder| override Flask's static and template directories.
|                 | app:template_folder| override Flask's static and template directories.
|                 | app:debug          | boolean for Flask debug mode. |
| web/app.py      | app:name| Flask app name used when constructing the `Flask(...)` app.|
|                 | app:static_folder| override Flask's static and template directories.
|                 | app:template_folder| override Flask's static and template directories.
|                 | app:debug          | boolean for Flask debug mode. |
| web/old-control.py| app:name| Flask app name used when constructing the `Flask(...)` app.|
|                 | app:static_folder| override Flask's static and template directories.
|                 | app:template_folder| override Flask's static and template directories.
|                 | app:debug          | boolean for Flask debug mode. |
|                 | serial.read_timeout | timeouts for pyserial read/write operations (seconds).|
|                 | serial.write_timeout| timeouts for pyserial read/write operations (seconds).|
|                 | serial.max_read_size| maximum bytes to read when expecting an initial response from the motor controller. |


