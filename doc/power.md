# Power Control

If you hit the power button, the ESP will loose power directly. Since the microcontroller is stateless that is OK. 
For the Raspberry which is used as host controlelr thats a different piece of cake. This Linux machine wants to be 
shutdown correctly to prevent data loss issues on the memory card. The below shutdown circuit feeds GPIO4 with a 
logical True. When the ESP drops power, GPIO4 will go to False, which is a signal for the PI to directly start the
shutdown sequence. The supercaps in the scheme will give the PI some time (seconds) to complete that task.

<img src="./pics/orover messaging-supercap.png" width="600" /> 

## Enable / disable

Update the config.ini file. Under section [processes] add the following line
::name:: = powercontrol.py

name can be any string, but suggest to user "powercontrol" or something similair.
After the change restart the oRover system.

If you want to disable the powercontrol script, simply remove the line.

## Parameters
Add the section [powercontrol] if not present in the file.

The scripts accepts the following parameters

| Param | Description |
|-------|-------------|
|pin = X| Pin number where the shutdown circuit is connected. Use BCM pin numbering. Default pin = 4 |
|sleep_time = X|Float, niumber of seconds to wait after first pull down of pin to prevent false signals. Default 2.0 seconds|