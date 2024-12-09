###########################################################################
#
#   Copyright (C) 2022 C v Kruijsdijk & P. Zengers
#
#   This program uses a built-in webserver to control a surveillance robot
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#   You can contact the authors via their git profile
#
###########################################################################

# Import standard modules
# from ast import If 
import sys
import os
import time
import io
import math

# We expect Python Version 3
if sys.version_info[0] < 3:
    sys.exit("This code is intended to run on Python V3 and higher. See README")    

# Check if flask is installed
from flask import Flask, render_template, Response, redirect, request
if 'flask' not in sys.modules:
    sys.exit("Flask is required but not found. See README")    

# Check if configparser is installed
import configparser
if 'configparser' not in sys.modules:
    sys.exit("'configparser' is required but not found. See README")    

# Check if serial is installed
import serial
if 'serial' not in sys.modules:
    sys.exit("'pyserial' is required but not found. See README")    

# Declare some globals
configfile_name = '../cfg/config.ini' # Where to find the global configuration
serial_open = False # Assume port not open yet
config = None       # No config retrieved yet
msg = ''            # Nothing to tell yet
ser = None          # Serial port

###########################################################################
def writeConfig(config,configfile_name):
    # Write all info to config.ini

    # Not finished
    return


###########################################################################
def readConfig(configfile_name):
    # Read all info from config.ini

    if not os.path.isfile(configfile_name):
        sys.exit("Configuration file does not exist")

    config = configparser.ConfigParser() 
    config.read(configfile_name)
    return config
    
   
###########################################################################
def calcMotorActions(ser,speed,x,y):
    # convert x and y angles to motor commands

    # MxxDySzz;           Change motor
    #                     xx = FL, FR, RL, RR (front, read, left, right)
    #                     y  = F, B (forward, backward)
    #                     zz = -99 <-> 99 as percentage of speed
    leftdirection = "F" # Init 
    rightdirection = "F" # Init 

    if speed == 0:
        command_stream = 'S;' 
     #% \
     #                ( leftdirection,  leftspeed ,
     #                  rightdirection, rightspeed,
     #                  leftdirection,  leftspeed,
     #                  rightdirection, rightspeed)

        try:
            ser.write(bytes(command_stream.encode()))
        except serial.SerialTimeoutException:
            serial_open = False
            return 'Motor controller did not accept the command'
#    return command_stream
        return "hello"  #motor(ser,"S")

    angle = round(math.degrees(math.atan2(x,y))) # degrees
    # angle will be netative if we go left, positve if we go right, 180 is full reverse
    # Correct by ensuring all in one circle
    if angle < 0:
        angle = 360 + angle 
 
    # convert angles to motor movements
    if angle >= 0 and angle <= 45:
        leftmotor = 1
        rightmotor = (45-angle) / 45.0

    if angle > 45 and angle <= 90:
        leftmotor = 1
        rightmotor = (45-angle) / 45.0
    
    if angle > 90 and angle <= 135:	 
        leftmotor = (135 - angle) / 45.0
        rightmotor = -1

    if angle > 135 and angle <= 180:
        leftmotor = (135 - angle)/45
        rightmotor = -1

    if angle > 180 and angle <= 225:
        leftmotor = -1
        rightmotor = (135 - angle)/45	
    
    if angle > 225 and angle <= 270:
        leftmotor = -1
        rightmotor = (135 - angle)/45	
    
    if angle > 270 and angle <= 315:
        leftmotor = (angle - 315)/45
        rightmotor = -1	
    
    if angle > 315 and angle <= 360:	 
        leftmotor = (angle - 315)/45	
        rightmotor = -1	

    # Determine direction for left and right motors
    if leftmotor < 0:
        leftdirection = "R"
    if rightmotor < 0:
          rightdirection = "R"
    
    # determine actual speed for left and right side
    leftspeed  = max(0,min(round(abs(leftmotor) * speed),99))
    rightspeed = max(0,min(round(abs(rightmotor) * speed),99))
    
    # execute command
    if ser == None:
        return "Serial port not open"

    command_stream = 'MFLD%sS%02.0f;MFRD%sS%02.0f;MRLD%sS%02.0f;MRRD%sS%02.0f;' % \
                     ( leftdirection,  leftspeed ,
                       rightdirection, rightspeed,
                       leftdirection,  leftspeed,
                       rightdirection, rightspeed)

    try:
        ser.write(bytes(command_stream.encode()))
    except serial.SerialTimeoutException:
        serial_open = False
        return 'Motor controller did not accept the command'
    return command_stream
    
##########################################################################
def openSerial():
    global msg
    serialConfig = config['serial']

    if serialConfig.get('port',None) == None:
        msg = 'Serial port to motor controller not configured' 
        return ser

    print('Serial port' + serialConfig.get('port',None))
    try:
        ser = serial.Serial(port = serialConfig.get('port',None),
                            baudrate = serialConfig.get('baudrate',9600),
                            timeout = serialConfig.get('read_timeout',2), 
                            write_timeout = serialConfig.get('write_timeout',2))
        time.sleep(2)

    except ValueError:
        msg = 'Check serial parameters, your config seems incomplete or incorrect'
        print(msg)
        return None

    except serial.SerialException: 
        msg = 'Device cannot be found or not configured'
        print(msg)
        return None

   # Arriving here, we know that the serial port is open
    try:
        ser.write(b'hello')
    except serial.SerialTimeoutException:
        msg = 'Motor controller did not receive the hello message'
        print(msg)
        return ser
    
    try:
        mc_answer = ser.read(serialConfig.get('max_read_size',99)) # max bytes configured
    except serial.SerialTimeoutException:
        msg = "Motor controller did not respond to hello message"
        print(msg)
        return ser
    
    msg = "Motor controller connected on port " + serialConfig.get("port",None)
# + \
#          " tells " + mc_answer
    print(msg)

    return ser


###########################################################################
# Init Main Program
###########################################################################
config  = readConfig(configfile_name)
ser = openSerial()


###########################################################################
# Web server
###########################################################################
if 'app' not in config:
    config.add_section('app')
appConfig = config['app']

app = Flask(appConfig.get('name','oRover'), 
            static_folder   = appConfig.get('static_folder','static'), 
            template_folder = appConfig.get('template_folder','template')
           )

app.config.update(
   DEBUG        = appConfig.getboolean('debug',True)
  )

@app.route('/')
def index():
    return render_template('index.html', topmsg=msg)

@app.route('/config')
def config():
    return "config not ready yet"

@app.route('/move')
def move():
    # Example received from page: move?speed=50&x=4&y=5
    try:
        speed = int(request.args.get('speed', 0))
        x = int(request.args.get('x', 0))
        y = int(request.args.get('y', 0)) 
    except:
        return "Parameter not an integer"
    
    if x > 100 or x < -100 or \
       y > 100 or y < -100 or \
       speed > 100 or speed < -100:
       return "Parameter value out of bound"
       
    return calcMotorActions(ser,speed,x,y)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
