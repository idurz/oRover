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

## 📂 Repository Structure
- orover     main directory
  - demos    some test script and unfinished small stuff
  - doc      detailled documentation
  - esp      esp software for the driver board
  - pi       pi software for the host computer

## Other resources
[Link to WaveShare folder](https://github.com/waveshareteam/ugv_base_general/tree/main)
