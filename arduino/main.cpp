/* ****************************************************************************
 *
 *   Copyright (C) 2022 C v Kruijsdijk & P. Zengers
 *
 *   This program uses a built-in webserver to control a surveillance robot
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *   You can contact the authors via their git profile
 *
 *****************************************************************************/

/* ****************************************************************************
 *
 * Serial Command list
 *
 * - Multiple commands in one line allowed
 * - Separate command with "|" 
 *
 * Commands defined
 * ----------------
 * S                   Stop all motors
 *
 * MxxDySzz            Change motor
 *                     xx = FL, FR, RL, RR (front, read, left, right)
 *                     y  = F, B (forward, backward)
 *                     zz = -99 <-> 99 as percentage of speed
 * 
 * V                   Request version info
 *
 *****************************************************************************/


/* ****************************************************************************
 * Include the necessary libraries here
 * ****************************************************************************/

#include <Arduino.h>
#include <AFMotor.h>

/* *****************************************************************************
   Defines, to ensure our code is easier to maintain
 * ****************************************************************************/

#define VERSION             "1.0.0"

// Serial port config
#define DEBUG_BAUDRATE      9600  // Hardware serial (USB)
#define CONTROLLER_BAUDRATE 9600  // Software serial to PI
#define END_OF_COMMAND      ';' 

// Motors
#define MOTOR_FRONT_LEFT_ID  2
#define MOTOR_FRONT_RIGHT_ID 1
#define MOTOR_REAR_LEFT_ID   3
#define MOTOR_REAR_RIGHT_ID  4

/* *****************************************************************************
   Global variables out of scope of functions
 * *****************************************************************************/

// (partly) commandstring received from Serial
String commandReceived = "";

// construct motor objects
AF_DCMotor mtr_front_left(MOTOR_FRONT_LEFT_ID);
AF_DCMotor mtr_front_right(MOTOR_FRONT_RIGHT_ID);
AF_DCMotor mtr_rear_left(MOTOR_REAR_LEFT_ID);
AF_DCMotor mtr_rear_right(MOTOR_REAR_RIGHT_ID);

/* *************************************************************************************************
   setup

   Run once
 * *************************************************************************************************/
void setup() {
  Serial.begin(DEBUG_BAUDRATE);           // set up Serial library at 9600 bps
  Serial1.begin(CONTROLLER_BAUDRATE);     // 
  while (!Serial) {
    ; // Wait for Serial to connect
  }
  Serial.println("oRover Actor Version " + String(VERSION));
}

/* *************************************************************************************************
   stopRobot

   Stop all motors
 * *************************************************************************************************/
void stopRobot() {
  // Stop all motors
  mtr_front_left.run(RELEASE);
  mtr_front_right.run(RELEASE);
  mtr_rear_left.run(RELEASE);
  mtr_rear_right.run(RELEASE);
}

/* *************************************************************************************************
   requestMotor

   Verify if valid motor command and if yes, execute
 * *************************************************************************************************/
void requestMotor(String commandReceived) {
  int direction = 0;
  String direction_Name = "";
  String name = "";
  int speed = 0;

  if (commandReceived.length() != 8) {
    Serial.println("Motor command ignored, not in format MxxDySzz. Length invalid");
    return;
  }
      
  // Check Speed parameter
  if (commandReceived.charAt(5) != 'S') {
    Serial.println("Motor command ignored, not in format MxxDySzz. Speed missing");
   return;
  }
  
  speed = commandReceived.substring(6,8).toInt();
  // Our speed received is a percentage. Set it to the range 0..255
  speed = map(speed, 0, 100, 0, 255);

  // Check Direction parameter
  if (commandReceived.charAt(3) != 'D') {
    Serial.println("Motor command ignored, not in format MxxDySzz. Direction missing");
    return;
  }
  if (commandReceived.charAt(4) != 'F') {
    direction = FORWARD;
    direction_Name = "forward";
  } else if (commandReceived.charAt(4) != 'B') {
    direction = BACKWARD;
    direction_Name = "backward";
  } else {
    Serial.println("Motor command ignored, not in format MxxDySzz. Direction invalid");
    return;
  }

  // Act on the motor command
  if        (commandReceived.substring(1,3) == "FL") {
    mtr_front_left.setSpeed(speed);
    mtr_front_left.run(direction);
    name = "Front Left";
  } else if (commandReceived.substring(1,3) == "FR") {
    mtr_front_right.setSpeed(speed);
    mtr_front_right.run(direction);
    name = "Front Right";
  } else if (commandReceived.substring(1,3) == "RL") {
    mtr_rear_left.setSpeed(speed);
    mtr_rear_left.run(direction);
    name = "Rear Left";
  } else if (commandReceived.substring(1,3) == "RR") {
    mtr_rear_right.setSpeed(speed);
    mtr_rear_right.run(direction);
    name = "Rear Right";
  } else {
    Serial.println("Motor command ignored, not in format MxxDySzz. Motor invalid");
    return;
  }

  Serial.println("Motor " + name + " going " + direction_Name + " at speed " + String(speed) + "/255");

}


/* *************************************************************************************************
   requestStop

   Verify Stop command and execute if correct
 * *************************************************************************************************/
void requestStop(String commandReceived) {
  // Check if command is valid
  if (commandReceived.length() > 2) {
    Serial.println("S - Stop command should not have extra paramters. Command ignored.");
    return;
  }

  stopRobot();
  Serial.println("All motors stopped");
}

/* *************************************************************************************************
   verifyCommand

   Read bytes from serial port if available
 * *************************************************************************************************/
void verifyCommand() {
  Serial.println("Command received -" + commandReceived + "-");

  if      (commandReceived.charAt(0) == 'S')
    requestStop(commandReceived);
  else if (commandReceived.charAt(0) == 'M')
    requestMotor(commandReceived);
  else if (commandReceived.charAt(0) == 'V')
    Serial1.println("V" + String(VERSION) + String(END_OF_COMMAND));
  else 
    Serial.println("Ignored unknown command -" + commandReceived.substring(0,1) + "- received");
  
  commandReceived = "";
}

/* *************************************************************************************************
   loop

   Run as long as power is available
 * *************************************************************************************************/
void loop() {
  char r;

  if (Serial1.available() > 0) {

    r = Serial1.read();
    if (r == END_OF_COMMAND) { 

      verifyCommand();
      commandReceived = ""; // Release buffer for next command

    } else 
      commandReceived += r;

  } // Serial1.available
  
} // loop