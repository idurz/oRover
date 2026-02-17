from flask import Flask, render_template, jsonify, request
from pi.ugv import *
import os
import sys
import time
import math
import csv
import json
import zmq # pyright: ignore[reportMissingImports]
import oroverlib as orover
import setproctitle


# read config and setup logging
config = orover.readConfig()
logger = orover.setlogger(config)
setproctitle.setproctitle(f"orover:{orover.getmodulename(config)}")

# setup flask app
app = Flask(orover.getmodulename(config)
           ,static_folder   = config.get("static_folder",   fallback="static")
           ,template_folder = config.get("template_folder", fallback="template")
          )

# globals
commands = []





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

    # run flask app
    app.run(debug=config.getboolean('debug',fallback=True)
           ,host=config.get("host",   fallback="localhost")
           )