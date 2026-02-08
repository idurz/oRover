import time
import RPi.GPIO as GPIO
from threading import Lock
from motor import send_cmd

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
time.sleep(2)

STOP_DISTANCE = 30  # cm
safety_state = "CLEAR"
state_lock = Lock()

#def read_radar():
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    while GPIO.input(ECHO) == 0:
        start = time.time()

    while GPIO.input(ECHO) == 1:
        end = time.time()
 
    duration = end - start
    distance = (duration * 34300) / 2 # cm
 #   print(f"Distance.... {distance} m")
    return round(distance, 2)

def radar_monitor(ser): 
    global safety_state

    while True:
        distance = get_distance()

        with state_lock:
            if distance <= STOP_DISTANCE:
                if safety_state != "STOPPED":
                    print(f"Distance..STOP.. {distance} m")
                    send_cmd(ser, 0, 0)
                    safety_state = "STOPPED"
            else:
                safety_state = "CLEAR"

        time.sleep(0.1)
