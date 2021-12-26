# oRover
oRover is an Observation Robot which you can send in your house to check what is happening. You can steer oRover via Internet and receive it's camera stream back to tell you what is happening. It is built with a Raspberry PI as central controller and an Arduino Mega to work with the motors and the sensors.

## Hardware
  *  Raspberry PI zero W as central controller
  *  Arduino Mega as sensor and motor controller
  *  Any robot chassis with four motors
  *  the Adafruit V1 motor shield or look-a-like

## Raspberry install
This repository assumes you have the skills to install a Raspberry and have a command shell via a SSH session. If you are relative new to this stuff you might check the [install guide](https://www.raspberrypi.com/documentation/computers/getting-started.html) to create a running PI. In this project we used a Raspberry Pi Zero, but if you have a PI3 or PI4 at hand that will work as well. Also [randomnerdtutorials](https://randomnerdtutorials.com/installing-raspbian-lite-enabling-and-connecting-with-ssh/) might be of great help.

## Python version
Check which python version you are running with the command:

`python --version`

  * If the answer started with "Python 3" -> You are done with this step; [start installing Flask](https://github.com/idurz/oRover/blob/main/README.md#instal-flask)
  * If the answer started with "Python 2" or the command failed try 

`python3 --version`

  * If the answer started with "Python 3" then we need to create an alias for your user. Check the answer from the command above. It starts with "Python 3." but we are interested in the next number. It can e.g. by "Python 3.4"  or "Python 3.7" Use that info to execute the following commands where the last number should be exactly the same as found in the result above. Example: the command above returns "Python 3.7.2". Then we will need "3.7" here. We will create an alias for that version with 

`alias python='/usr/bin/python3.7'`

`. ~/.bashrc`

Note that the last number is dependant on the answer from the previous command.

  * If command failed you need to install python3 on your PI with

`sudo apt install python3`

after the install completes succcesfully, restart this step.

## Install PIP
PIP is the Python package processor. We need to install this to complete the next step. This is a Python script that uses some bootstrapping logic to install pip.

Download the script, from https://bootstrap.pypa.io/get-pip.py.

`python get-pip.py`

## Instal Flask
The webserver we use to control oRover is designed around [Flask](https://palletsprojects.com/p/flask/). Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around Werkzeug and Jinja and has become one of the most popular Python web application frameworks. 

If not already present, install Flak in your PI with the following commands.

`pip3 install -U Flask`

## Instal pyserial
The oRover webserver communicates with the Arduino motor controller via a serial port. If not already present, install pySerial in your PI with the following commands.

`pip3 install pyserial`

## Install oRover
After completing the above Flask step we have all the conditions met to install the oRover web server. Download the code with

`git clone https://github.com/idurz/oRover.git`

Now install the webserver on the PI

`bla bla` 


