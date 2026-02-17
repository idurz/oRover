# UGV interface

## Background

The UGV interface is a critical component that bridges the gap between high-level commands (e.g., from a web interface 
or controller) and low-level hardware interactions (e.g., motor control, sensor readings) via the [driver board](driverboard). It subscribes to commands via ZeroMQ, 
translates them into serial commands for the hardware, and publishes feedback back to ZeroMQ for other components to consume.

## Setup

The high-level setup looks like this:
```

┌───────────┐      ZMQ SUB       ┌────────-────┐      Serial TX
│ BOSS      │ ────────────────▶  │ UGV         │ ─────────────▶ ESP32 robot hardware
| controller|                    | bridge      |                      * Optional LIDAR interface         
└───────────┘                    │ service     │                      * IIC expansion
                                 │             │                      * INA219 voltage monitoring
                                 │ driverboard │                      * ST3215 bus servo interface
                                 |             |                      * Motor interface with encoders
┌───────────┐      ZMQ PUB       |             |                      * AK09918C 3-axis electronic compass
│ Consumers │ ◀────────────────  │             │ ◀──────────── ESP32 robot hardware
└───────────┘                    └────-────────┘      Serial RX
```

This script needs to work with non-blocking I/O everywhere, both serial and zmq by using a single poll/select loop. In this way we avoid threads. With threads there is the risk of race conditions, locking and shutdown complexity. Multiprocessing adds weight to the process, and AsyncIO adds additional complexity.
