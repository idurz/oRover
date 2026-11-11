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

Our development engine is a 64-bit Pi Zero 2W running Debian Trixie. A Debian-based Raspberry Pi system with systemd, internet access and sudo is required.

Download and run the installer as the user that will run the robot:

```bash
curl -fsSLo install.sh https://raw.githubusercontent.com/idurz/oRover/main/install.sh
bash install.sh
```

The installer clones into `~/oRover`, installs the Python dependencies, and enables the systemd service for future boots. Pass a directory as an argument to choose another location. It creates `/etc/orover/config.ini`, migrating an existing `pi/config.ini` when present. Running it again fast-forwards the existing checkout and preserves the system configuration; it stops if Git cannot update safely.

Review `/etc/orover/config.ini` and hardware access before starting the service with `sudo systemctl start orover`. The service runs as the installing user, who needs access to the configuration, serial device and GPIO. See [systemd setup](doc/systemd.md) for details.

For `/dev/serial0`, the installer disables serial login and enables the Raspberry Pi UART when `raspi-config` is available. This may require a reboot and removes serial-console login access.


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

## Recent update (2026-06-15)

- Added a live debug log page at `/debug` that follows the active `orover.log` file.
- The debug page now supports filtering by source, level, and keyword, with source choices driven from the `[scripts]` section of `config.ini`.
- A Pause/Resume button lets you stop auto-refresh while inspecting a specific log point.
- The debug layout was compacted so the message column has more room.

## Recent update (2026-11-11)

- Added an embedded live navigation grid with resolution and origin information.
- Added an installer for Git updates, Python dependencies, and systemd service setup.
- Standardized runtime configuration at `/etc/orover/config.ini`, preserving existing settings during installation.
- Added serial access setup for `dialout` and Raspberry Pi UART configuration when using `/dev/serial0`.
- UGV serial errors are reported to the application log and systemd journal before the process exits.
- Updated launcher shutdown reporting and added installer and serial-error tests.

## Start and stop

From the `pi/` directory:

```bash
PATH="$PWD/.venv/bin:$PATH" ./start  # starts launcher.py in the background
PATH="$PWD/.venv/bin:$PATH" ./stop   # sends cmd.shutdown through the event bus
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
