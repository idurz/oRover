# Command set
Commands send from the PI, or via the UGV own web interface are translated to JSON commands which are processed by the software. See [uart_ctrl](../esp/include/uart_ctrl.h)
See also [JSON Commands](https://www.waveshare.com/wiki/UGV01#JSON_Command_Set) for a description of some of the commands.

## Format
A JSON command will follow this format:
{"T":<T_code>,"param1":<param1value>,"param2":<param2value>,........."paramN":<paramNvalue>}	

The T_code and the parameters can be found in the below table.

## Example

  * To delay the timing you can use command CMD_DELAY_MILLIS. 
  * That translates to T_code 111. 
  * A parameter with the cmd is required which specifies the amount of ms to delay.
  * If you want to delay with 3 seconds, your command should be:

```
{"T":111,"cmd":3000}
```

## List of known commands

Source of truth: [esp/include/json_cmd.h](../esp/include/json_cmd.h)

### UGV, module, IMU and feedback

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_SPEED_CTRL|1|L, R|Wheel speed control in m/s.|
|CMD_SET_MOTOR_PID|2|P, I, D, L|Set motor PID values (L reserved for windup limit).|
|CMD_OLED_CTRL|3|lineNum, Text|Write text to OLED line 0..3.|
|CMD_OLED_DEFAULT|-3|-|Restore default OLED screen.|
|CMD_MODULE_TYPE|4|cmd|Set module type (0 none, 1 arm, 2 gimbal).|
|CMD_PWM_INPUT|11|L, R|Direct PWM input (-255..255), mainly for debug.|
|CMD_ROS_CTRL|13|X, Z|Linear/angular control (m/s, rad/s).|
|CMD_EOAT_TYPE|124|mode|Set end-of-arm type (gripper/wrist).|
|CMD_CONFIG_EOAT|125|pos, ea, eb|Configure EoAT geometry offsets.|
|CMD_GET_IMU_DATA|126|-|Request IMU data.|
|CMD_CALI_IMU_STEP|127|-|Start IMU calibration (keep robot still).|
|CMD_GET_IMU_OFFSET|128|-|Read IMU offset.|
|CMD_SET_IMU_OFFSET|129|x, y, z|Set IMU offset.|
|CMD_BASE_FEEDBACK|130|-|One-shot chassis feedback (L, R, r, p, y, v).|
|CMD_BASE_FEEDBACK_FLOW|131|cmd|Enable/disable continuous chassis feedback.|
|CMD_LED_CTRL|132|IO4, IO5|PWM output control for IO4/IO5.|
|CMD_GIMBAL_CTRL_SIMPLE|133|X, Y, SPD, ACC|Simple gimbal angle control.|
|CMD_GIMBAL_CTRL_MOVE|134|X, Y, SX, SY|Gimbal move with axis speed values.|
|CMD_GIMBAL_CTRL_STOP|135|-|Stop gimbal movement.|
|CMD_HEART_BEAT_SET|136|cmd|Set heartbeat period in ms.|
|CMD_GIMBAL_STEADY|137|s, y|Enable/disable stabilization modes.|
|CMD_SET_SPD_RATE|138|L, R|Set speed scaling factors.|
|CMD_GET_SPD_RATE|139|-|Read speed scaling factors.|
|CMD_SAVE_SPD_RATE|140|-|Persist speed scaling factors.|
|CMD_GIMBAL_USER_CTRL|141|X, Y, SPD|Incremental gimbal user control.|
|CMD_FEEDBACK_FLOW_INTERVAL|142|cmd|Set delay interval for feedback stream (ms).|
|CMD_UART_ECHO_MODE|143|cmd|Serial echo of received commands on/off.|
|CMD_ARM_CTRL_UI|144|E, Z, R|UI control channel for arm module.|

### Arm and EoAT control

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_MOVE_INIT|100|-|Initialize/move arm to initial state.|
|CMD_SINGLE_JOINT_CTRL|101|joint, rad, spd, acc|Control one joint in radians.|
|CMD_JOINTS_RAD_CTRL|102|base, shoulder, elbow, hand, spd, acc|Control all joints in radians.|
|CMD_SINGLE_AXIS_CTRL|103|axis, pos, spd|Move one Cartesian axis.|
|CMD_XYZT_GOAL_CTRL|104|x, y, z, t, spd|Cartesian goal control with interpolation.|
|CMD_SERVO_RAD_FEEDBACK|105|-|Read arm pose/torque feedback.|
|CMD_EOAT_HAND_CTRL|106|cmd, spd, acc|Control hand/gripper joint angle.|
|CMD_EOAT_GRAB_TORQUE|107|tor|Set grab torque.|
|CMD_SET_JOINT_PID|108|joint, p, i|Set per-joint PID values.|
|CMD_RESET_PID|109|-|Reset PID to defaults.|
|CMD_SET_NEW_X|110|xAxisAngle|Set a new x-axis reference.|
|CMD_DELAY_MILLIS|111|cmd|Delay execution by ms.|
|CMD_DYNAMIC_ADAPTATION|112|mode, b, s, e, h|Enable/disable dynamic external-force adaptation.|
|CMD_SWITCH_CTRL|113|pwm_a, pwm_b|Switch 12V control (non-UGV).|
|CMD_LIGHT_CTRL|114|led|Light level control (non-UGV).|
|CMD_SWITCH_OFF|115|-|Switch off (non-UGV).|
|CMD_SINGLE_JOINT_ANGLE|121|joint, angle, spd, acc|Control one joint in degrees.|
|CMD_JOINTS_ANGLE_CTRL|122|b, s, e, h, spd, acc|Control all joints in degrees.|
|CMD_CONSTANT_CTRL|123|m, axis, cmd, spd|Continuous incremental control mode.|
|CMD_XYZT_DIRECT_CTRL|1041|x, y, z, t|Direct Cartesian set (no interpolation).|

### File and mission editing

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_SCAN_FILES|200|-|List files in flash.|
|CMD_CREATE_FILE|201|name, content|Create a file with initial content.|
|CMD_READ_FILE|202|name|Read file content.|
|CMD_DELETE_FILE|203|name|Delete a file.|
|CMD_APPEND_LINE|204|name, content|Append one line to file.|
|CMD_INSERT_LINE|205|name, lineNum, content|Insert one line at index.|
|CMD_REPLACE_LINE|206|name, lineNum, content|Replace one line at index.|
|CMD_READ_LINE|207|name, lineNum|Read one line at index.|
|CMD_DELETE_LINE|208|name, lineNum|Delete one line at index.|
|CMD_TORQUE_CTRL|210|cmd|Torque lock on/off.|
|CMD_CREATE_MISSION|220|name, intro|Create mission metadata.|
|CMD_MISSION_CONTENT|221|name|Read mission full content.|
|CMD_APPEND_STEP_JSON|222|name, step|Append JSON step to mission.|
|CMD_APPEND_STEP_FB|223|name, spd|Append step from current feedback.|
|CMD_APPEND_DELAY|224|name, delay|Append delay step (ms).|
|CMD_INSERT_STEP_JSON|225|name, stepNum, step|Insert JSON step.|
|CMD_INSERT_STEP_FB|226|name, stepNum, spd|Insert feedback-based step.|
|CMD_INSERT_DELAY|227|name, stepNum, delay|Insert delay step.|
|CMD_REPLACE_STEP_JSON|228|name, stepNum, step|Replace step with JSON step.|
|CMD_REPLACE_STEP_FB|229|name, stepNum, spd|Replace step with feedback step.|
|CMD_REPLACE_DELAY|230|name, stepNum, delay|Replace step with delay step.|
|CMD_DELETE_STEP|231|name, stepNum|Delete mission step.|
|CMD_MOVE_TO_STEP|241|name, stepNum|Move robot to mission step.|
|CMD_MISSION_PLAY|242|name, times|Run mission n times (-1 for loop).|

### ESP-NOW

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_BROADCAST_FOLLOWER|300|mode, mac|Configure follower broadcast behavior.|
|CMD_ESP_NOW_CONFIG|301|mode|Set ESP-NOW mode.|
|CMD_GET_MAC_ADDRESS|302|-|Read device MAC address.|
|CMD_ESP_NOW_ADD_FOLLOWER|303|mac|Add ESP-NOW peer.|
|CMD_ESP_NOW_REMOVE_FOLLOWER|304|mac|Remove ESP-NOW peer.|
|CMD_ESP_NOW_GROUP_CTRL|305|dev, b, s, e, h, cmd, megs|Send grouped follower control/data.|
|CMD_ESP_NOW_SINGLE|306|mac, dev, b, s, e, h, cmd, megs|Send single/broadcast control/data.|

### WiFi

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_WIFI_ON_BOOT|401|cmd|Set boot WiFi mode (off/AP/STA/AP+STA).|
|CMD_SET_AP|402|ssid, password|Configure AP credentials.|
|CMD_SET_STA|403|ssid, password|Configure STA credentials.|
|CMD_WIFI_APSTA|404|ap_ssid, ap_password, sta_ssid, sta_password|Configure AP+STA mode.|
|CMD_WIFI_INFO|405|-|Read current WiFi status/config.|
|CMD_WIFI_CONFIG_CREATE_BY_STATUS|406|-|Create wifiConfig.json from running status.|
|CMD_WIFI_CONFIG_CREATE_BY_INPUT|407|mode, ap_ssid, ap_password, sta_ssid, sta_password|Create wifiConfig.json from input values.|
|CMD_WIFI_STOP|408|-|Disconnect/stop WiFi.|

### Servo and device management

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|CMD_SET_SERVO_ID|501|raw, new|Change a servo ID.|
|CMD_SET_MIDDLE|502|id|Set current pose as servo middle.|
|CMD_SET_SERVO_PID|503|id, p|Set servo P/PID value.|
|CMD_REBOOT|600|-|Reboot ESP32.|
|CMD_FREE_FLASH_SPACE|601|-|Report free flash size.|
|CMD_BOOT_MISSION_INFO|602|-|Read boot mission settings.|
|CMD_RESET_BOOT_MISSION|603|-|Clear boot mission settings.|
|CMD_NVS_CLEAR|604|-|Erase NVS storage.|
|CMD_INFO_PRINT|605|cmd|Set serial debug print mode.|
|CMD_MM_TYPE_SET|900|main, module|Set platform main/module type.|

### Feedback/event messages from ESP

|Command|T_code|Parameters|Description|
|---|---:|---|---|
|FEEDBACK_BASE_INFO|1001|varies|Base information feedback payload.|
|FEEDBACK_IMU_DATA|1002|varies|IMU feedback payload.|
|CMD_ESP_NOW_RECV|1003|mac, megs|ESP-NOW receive event.|
|CMD_ESP_NOW_SEND|1004|mac, status, megs|ESP-NOW send status event.|
|CMD_BUS_SERVO_ERROR|1005|id, status|Bus servo error feedback.|
