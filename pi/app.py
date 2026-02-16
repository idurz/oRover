from flask import Flask, render_template, jsonify, request
from motor import *
import os
import sys
import time
import argparse
import math
import csv
import json
import zmq # pyright: ignore[reportMissingImports]
import pi.oroverlib as orover

# Check if configparser is installed
import configparser
if 'configparser' not in sys.modules:
    sys.exit("'configparser' is required but not found. See README")    

# Declare some globals
configfile_name = '../cfg/config.ini' # Where to find the global configuration
config = None       # No config retrieved yet
msg = ''            # Nothing to tell yet
#socket = None # global socket

commands = []

global socket
# open zmg
socket = orover.connect_to_server()


def rx_commands():
    #open file and fill commands
    commands.clear()
    with open("commands.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            commands.append((float(row["distance"]), float(row["angle"])))

#    ser = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # allow UART to settle

    #execute commands
    for distance, angle in commands:
        print(f"Driving {distance} m")
#        drive_straight(ser, distance)                       ombouwen naar socket

        time.sleep(0.5)

        print(f"Turning {angle} degrees")
 #       rotate(ser, angle)                                 ombouwen naar socket

    print("Done.")

app = Flask(__name__)

# Example runtime state (in real use, replace with sensor reads / hardware control)
state = {
    "temperature": 22.5,
    "speed": 0.0,
    "angle": 0.0,
    "voltage": 12.6
}
###########################################################################
def readConfig(configfile_name):
    # Read all info from config.ini

    if not os.path.isfile(configfile_name):
        sys.exit("Configuration file does not exist")

    config = configparser.ConfigParser() 
    config.read(configfile_name)
    return config

###########################################################################
# Init Main Program
###########################################################################
config  = readConfig(configfile_name)

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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/control", methods=["POST"])
def control():
    data = request.get_json() or {}
    action = data.get("action")
    # Handle actions: forward, back, left, right
    # Replace the following with your actual control logic
    # Map actions to motor speeds
    if action == "forward":
        left_speed = 0.5
        right_speed = 0.5
    elif action == "back":
        left_speed = -0.5
        right_speed = -0.5
    elif action == "left":
        left_speed = -0.3
        right_speed = 0.3
    elif action == "right":
        left_speed = 0.3
        right_speed = -0.3
    else:
        return {"error": f"Unknown action: {action}"}, 400

    # Send command to BOSS
    answer = orover.send(
        socket,
        src=orover.controller.remote_interface,       # Who is sending
        reason=orover.cmd.set_motor_speed,      # Must be a command enum (2000-range)
        body={"left_speed": left_speed, "right_speed": right_speed}
    )

    if answer:
        print(f"Boss told me {answer}")

    return jsonify({"status": "unknown action"}), 400

    # Example: small temp/voltage drift to show changes
    state["temperature"] += 0.01
    state["voltage"] -= 0.001

    return jsonify({"status": "ok", "action": action, "state": state})

@app.route("/status")
def status():
    # Return current values for frontend to display
    return jsonify({
        "temperature": round(state["temperature"], 2),
        "speed": round(state["speed"], 2),
        "angle": round(state["angle"], 2),
        "voltage": round(state["voltage"], 2)
    })

@app.route("/readroute", methods=["POST"])
def readroute():
    rx_commands()
    return jsonify(status="route processed")

# -----------------------------
# Route processing (NEW)
# -----------------------------
@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()
    route = data.get('route', [])

    if not route:
        return jsonify(error="No route provided"), 400

    print("Received route:")
    for i, step in enumerate(route):
        distance = step.get('distance')
        angle = step.get('angle')
        print(f" Step {i+1}: distance={distance}, angle={angle}")

    # Save route to CSV
    with open("commands.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["distance", "angle"])
        writer.writeheader()
        writer.writerows(route)

   #open file and fill commands
    rx_commands()

    return jsonify(status="route accepted", steps=len(route))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
