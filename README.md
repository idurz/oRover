# WaveShare UGV Autonomous Robot (ESP32 + Raspberry Pi 5)

This repository contains the software stack for an **autonomous WaveShare UGV Tracked Robot**, combining a **real-time ESP-based microcontroller** with a **Raspberry Pi 5** for high-level control, AI vision, and autonomy.

The goal of this project is to explore **autonomous navigation**, **computer vision**, and **edge AI**, using affordable off-the-shelf hardware.

---

## 🚀 Project Goals

This is a learning project.

- Autonomous driving of a tracked UGV platform
- AI-based vision (object detection, tracking, lane/path following)
- Clear separation between **real-time motor control** and **high-level intelligence**
- Modular and extensible architecture
- Open and reproducible experimentation platform

---

## 🧠 System Architecture

### Role Separation

**ESP (Microcontroller)**
- Motor control (tracks)
- Encoder reading
- Low-level safety logic
- Deterministic real-time behavior

**Raspberry Pi 5**
- AI vision processing
- Autonomous navigation logic
- Sensor fusion
- Mission planning
- User interface / remote control
- Data logging

---

## 🧩 Hardware
A [WaveShare UGV Tracked Robot] (https://www.waveshare.com/wiki/UGV01)
 
![Driver board](General_Driver_for_Robot02.jpg)

  
|No.|Onboard Resources                                                    |
|--:|:--------------------------------------------------------------------|
|  1|ESP32-WROOM-32 main controller                                       |
|  2|IPEX1 WiFi connectoR                                                 |
|  3|LIDAR interface OPTIONAL Integrated radar adapter board function     |
|  4|IIC peripheral expansion interface	                                  |
|  5|Reset button	                                                      |
|  6|Download button	                                                  |
|  7|DC-DC 5V voltage regulator circuit	for host computers                |
|  8|Type-C connector (LIDAR)	LIDAR data interface                      |
|  9|Type-C connector (USB)	ESP32 UART communication interface            |
| 10|XH2.54 power port	Input DC 7~13V, Serial bus servo and motor        |
| 11|[INA219](https://github.com/wollewald/INA219_WE) Voltage/current monitoring chip                               |
| 12|Power ON/OFF	                                                      |
| 13|ST3215 serial bus servo interface	                                  |
| 14|Motor interface PH2.0 6P Group B interface for motor with encoder    |
| 15|Motor interface PH2.0 6P Group A interface for motor with encoder    |
| 16|Motor interface PH2.0 2P Group A interface for motor without encoder |
| 17|Motor interface PH2.0 2P Group B interface for motor without encoder |
| 18|AK09918C 3-axis electronic compass                                   |
| 19|QMI8658 6-axis motion sensor                                         |
| 20|TB6612FNG	Motor control chip                                        |
| 21|Serial bus servo control circuit	                                  |
| 22|SD card slot Can be used to store logs or WIFI configurations        |
| 23|40PIN extended header. Easy access to Raspberry Pi                   |
| 24|40PIN extended header.Easy to use the pins of the driver computer    |
| 25|CP2102	UART to USB for radar data transfer                           |
| 26|CP2102	UART to USB for ESP32 UART communication                      |
| 27|Automatic download circuit                                           |                         


---

## 📂 Repository Structure

- orover     main directory
  - demos    some test script and unfinished small stuff
  - esp      esp software for the driver board
  - pi       pi software for the host computer




# Other resources
[Link to WaveShare folder](https://github.com/waveshareteam/ugv_base_general/tree/main)

