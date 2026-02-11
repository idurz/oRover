# Driver board

## Summmary

Out of the box you'll find a chassis, with wheels/tracks and motors. A realtime controller based on an ESP32 is in the box as well. Sensors are build in for temperature and voltage control. Space for batteries and a 5V UPS like device is built in the chasssis. Power is used for the ESP, the motors and other (optional) components. 

Some connectors from the driver board are fed outside the chassis. These connectos are available to the host controller, e.g. a Raspberry PI.
Avaible:
  * 5V
  * GND
  * TX
  * RX
  * SCL
  * SDA

## Driver board

 The UGV comes with a driver board, see picture below:

<img src="./pics/General_Driver_for_Robot02.jpg" width="600" /> 

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

## Software

See also [JSON Commands](https://www.waveshare.com/wiki/UGV01#JSON_Command_Set)

|Command|JSON syntax|Description                                                  |
|-------|-----------|--------|
|Wheel speed control| {"T":1,"L":<speed>,"R":<speed>}|<speed> range -0.5 ~ +0.5 for right and left wheel. Unit m/s|
|PWM motor control  |{"T":11,"L":<range>,"R":<range>}|<range> range -255 ~ +255. Suggested is to use this command only for debugging. For speed control you should use "Wheel speed control" above|
|ROS Control        |{"T":13,"X":<velocity>,"Z":<rad>}|X is the velocity in m/s and the Z value is the steering angular velocity in rad/s.|
|Setting Motor PID  |{"T":2,"P":<val>,"I":<val>,"D":<val>,"L":<val>}|The three values of P, I and D correspond to proportional, integral and differential coefficients respectively, and the value of L is the interface reserved for Windup Limits, which is not available for the default PID controller used in UGV01 at present, and we have reserved this interface to facilitate the replacement of other PID controllers by users.|
|OLED Screen Setting|{"T":3,"lineNum":<nr>,"Text":"putYourTextHere"}|OLED screen display content settings, lineNum parameter for the line settings, can be: 0, 1, 2, 3, a total of 4 lines of content can be displayed. Each time you set a line of content, the new content will not affect the other lines of content displayed but will replace the original content before this line. The Text parameter is for the content setting where you can enter text that will be displayed on the corresponding line. After using this command, the OLED screen will not display the robot information, and display the content that the command lets it display.|
|Restore OLED Screen|{"T":-3}|When the command type is -3, the OLED screen will be restored to the initial status, and the robot information will be displayed.|
|Retrieve IMU Data|{"T":126}|Used to obtain IMU information, including heading angle, geomagnetic field, acceleration, attitude, temperature, etc.|
|Retrieve Chassis Information Feedback|{"T":130,"cmd":<x>}|Serial Port Continuous Feedback|x=0 turn off (default),x=1 (turn on). When this function is not enabled, the chassis information feedback is realized through a question-and-answer method, and the above CMD_BASE_FEEDBACK and so on are used to get the chassis information feedback. When this function is enabled, the chassis can continuously feedback information, and not need to query through the host, suitable for the ROS system.|
|Serial Port Echo Switch|{"T":143,"cmd":<x>}|<x>=0 off, <x>=1 on. When turned on, all the commands you send to the slave will appear in the serial port feedback.|
|IO4 IO5 Control|{"T":132,"IO4":<val>,"IO5":,<val>}|For setting the PWM of IO4 and IO5.|
|External Module Models|{"T":4,"cmd":<x>}|x=0: Null - 1: RoArm-M2 - 3: Gimbal|
|Pan-tilt Control|{"T":133,"X":45,"Y":45,"SPD":0,"ACC":0}|If the product is installed with a pan-tilt, it can be controlled by this command. The X value is the horizontal angle, the positive value is to the left, and the negative value is to the right. The Y value is the vertical angle, the positive value is up, and the negative value is down.|