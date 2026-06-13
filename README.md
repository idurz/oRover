# WaveShare UGV Autonomous Robot (ESP32 + Raspberry Pi 5)

This repository contains the software stack for an **autonomous WaveShare UGV Tracked Robot**, combining a **real-time ESP-based microcontroller** with a **Raspberry Pi** for high-level control, AI vision, and autonomy.

The goal of this project is to explore **autonomous navigation**, **computer vision**, and **edge AI**, using affordable off-the-shelf hardware.

---

## 🚀 Project Goals

- Learning from the below topics
- Autonomous driving of a tracked UGV platform
- AI-based vision (object detection, tracking, lane/path following)
- Clear separation between **real-time motor control** and **high-level intelligence**
- Modular and extensible architecture
- Open and reproducible experimentation platform

---

## Prerequisites

Install the following libraries before attempting to start oRover:

```
sudo apt install python3-serial
sudo apt install python3-zmq
sudo apt install python3-setproctitle
sudo apt install python3-flask
```

## Detailed documentation

Please follow link to [Technical Documentation](doc/technical%20documentation.md) for more information.

## Recent update (2026-06-04)

- Web telemetry rendering in the browser was hardened to safely handle non-numeric IMU/battery fields.
- IMU (`heading`, `pitch`, `roll`) and battery (`voltage`) values are now normalized before formatting, preventing `toFixed` runtime failures.
- Invalid or missing values now render as `--` instead of breaking the update loop.

## Recent update (2026-06-12)

- Added reusable bus integration tests in `pi/test/` for `boss.py`, `ugv.py`, `app.py`, `stop.py`, and `launcher.py`.
- The tests share a common helper library so new bus scenarios can be added without duplicating PUB/SUB setup or message formatting.
- See [pi/test/README_bus_tests.md](pi/test/README_bus_tests.md) for run examples and scenario coverage.

## Start and stop

From the `pi/` directory:

```bash
./start            # starts launcher.py in the background
./stop             # sends cmd.shutdown through the event bus
```

Use `./start <config.ini>` or `./stop <config.ini>` to select another config file.

## 📂 Repository Structure
- orover     main directory
  - demos    some test script and unfinished small stuff
  - doc      detailled documentation
  - esp      esp software for the driver board
  - pi       pi software for the host computer

## Other resources
[Link to WaveShare folder](https://github.com/waveshareteam/ugv_base_general/tree/main)
