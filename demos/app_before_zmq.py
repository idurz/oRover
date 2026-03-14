from flask import Flask, render_template, jsonify, request
from ugv import *
import os
import sys
import time
import math
import csv
import json
import zmq # pyright: ignore[reportMissingImports]
import oroverlib as orover
import setproctitle
import logging
import logging.handlers


def getmodulename(config):
    # Returns the name of the current module, based on the filename of the script, or the name defined in the config file if it matches the current 
    # script name. This allows for more flexible naming of processes in the config file
    if sys.argv[0] in config.items('scripts'): # sys.argv[0] contains the name of the currently running script, no path and with ".py" extension.
        print(f"Found script name {sys.argv[0]} in config, using corresponding name {config.get('scripts',sys.argv[0])} for logging")
        for name, path in config.items('scripts'): # find item in config that matches the current script name and return the key (name) of that item
            if sys.argv[0] == os.path.basename(path):
                return name
        return "default"  # default name if not found in config
    return sys.argv[0].split('.')[0]


def setlogger(config,myname):
    # Set up logging to send log messages to the boss process via a socket handler
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler('localhost',
                     logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    rootLogger.addHandler(socketHandler)
    logger = logging.getLogger(myname)

    loglevel = config.get('orover','loglevel',fallback="UNKNOWN").upper()
    known_level = (loglevel in ["DEBUG","INFO","WARNING","ERROR","CRITICAL"])
    if not known_level:
        logger.setLevel("ERROR")
        logger.error((f"Invalid log level {loglevel} in config, defaulting to 'ERROR'"))
    else:
        logger.setLevel(loglevel.upper())
    
    return logger


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



###########################################################################
# Web server
###########################################################################
config = orover.readConfig() # read config and setup logging
app = Flask(getmodulename(config) 
           ,static_folder   = config.get("app","static_folder",   fallback="static")
           ,template_folder = config.get("app", "template_folder", fallback="template"))
commands = [] # globals


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
    #state["temperature"] += 0.01
    #state["voltage"] -= 0.001

    #return jsonify({"status": "ok", "action": action, "state": state})


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



#### Main execution starts here ####
if __name__ == "__main__":

    logger = setlogger(config,getmodulename(config))
    setproctitle.setproctitle(f"orover:{getmodulename(config)}")

    # run flask app
    logger.info(f"Starting Flask app with debug={config.getboolean('app','debug',fallback=True)}, host={config.get('app','host',fallback='localhost')}, port={config.getint('app','port',fallback=5000)}")
    #app.run(debug=config.getboolean("app","debug",fallback=True)
    #       ,host=config.get("app","host",fallback="localhost")
    #       ,port=config.getint("app","port",fallback=5000)
    #       )
    app.run(debug=True, host="0.0.0.0", port=5000)