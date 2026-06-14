import sys

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import oroverlib as orover
import json
import uuid
import threading
import csv
import os
import sys
from base_process import baseprocess, handler


state = {"temperature": 22,
        "speed": 13,
        "angle": 0,
        "voltage": 14}

shared_state = {
    "map": {},
    "robot": {},
}

###########################################################################
# Handlers
###########################################################################

class handler:
    """ Contains the handlers for messages. Each handler takes a message as input and returns a result string. 
        The handlers are called by the BOSS server when a message with the corresponding reason is received.
        Handlers do not return a response to the sender, but can perform actions based on the message content, 
        like logging or sending new messages to the bus.

        Each message is expected to have the following structure:

            "id"    : UUID
           ,"ts"    : datetime of message in '%Y-%m-%dT%H:%M:%S.%f' format
           ,"src"   : message source, e.g. specific sensor or actuator, should be in class origin
           ,"me"    : sending script name
           ,"host"  : sending node
           ,"prio"  : priority of message, should be in class priority
           ,"reason": type of message, should be in class origin, state, event, origin, actuator, controller, priority, cmd
           ,"body"  : JSON; contains parameters depending on type of message
    """

    def __init__(self):
        # Stuff to send to the browser will be collected in this shared state dict, which handlers 
        # can update and the emit_function will send to the frontend every few seconds.
        pass

    def _as_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
        

    def event_heartbeat(self, msg):
        if "me" in msg and "ts" in msg:
            p.logger.info(f"Heartbeat received from {msg['me']} at {msg['ts']}")
            socketio.emit("heartbeat", {"me": msg["me"], "ts": msg["ts"]})
            return True
        else:
            p.logger.warning("Received heartbeat message missing 'me' or 'ts' fields")
            return False
    

    def state_battery(self, msg):
        voltage = msg.get("body", {}).get("voltage")
        p.logger.info(f"Battery data - Voltage: {voltage} V")
        socketio.emit("battery", {"voltage": voltage})
        return True
        

    def state_motion(self, msg): 
        # Example handler for IMU state messages, expects body to contain "heading", "pitch", and "roll" fields
        heading = msg.get("body", {}).get("heading")
        pitch = msg.get("body", {}).get("pitch")
        roll = msg.get("body", {}).get("roll")
        if heading is not None and pitch is not None and roll is not None:
            p.logger.info(f"IMU data - Heading: {heading} deg, Pitch: {pitch} deg, Roll: {roll} deg")
            socketio.emit("imu", {"h": heading, "p": pitch, "r": roll})
            return True
        else:
            p.logger.warning("Received IMU state message without required fields")
            return False


    def state_pose(self, msg):
        # Read-only navigation snapshot updates from navigation process.
        body = msg.get("body", {})
        if not isinstance(body, dict):
            p.logger.warning(f"Discarding pose update: invalid body type {type(body)}")
            return False

        # Canonical pose payload shape is body.pose.{x_m,y_m,heading_deg}.
        # Keep backward compatibility with older flat body.{x_m,y_m,heading_deg} payloads.
        pose_obj = body.get("pose", body)
        if not isinstance(pose_obj, dict):
            p.logger.warning("Discarding pose update: body.pose is not an object")
            return False

        x = self._as_float(pose_obj.get("x_m"))
        y = self._as_float(pose_obj.get("y_m"))
        h = self._as_float(pose_obj.get("heading_deg"))
        if x is None or y is None or h is None:
            p.logger.warning(f"Discarding pose update: non-numeric pose values in {pose_obj}")
            return False

        payload = {"x": x, "y": y, "h": h}
        pose_ts = body.get("ts", msg.get("ts"))
        if pose_ts is not None:
            payload["ts"] = pose_ts

        # Forward optional preview grid when present so grid.html can render map cells.
        preview = body.get("grid", {}).get("preview")
        if isinstance(preview, list) and (len(preview) == 0 or isinstance(preview[0], list)):
            payload["grid"] = {"preview": preview}
            shared_state["map"] = preview

        shared_state["robot"] = [x, y, h]

        p.logger.info(f"Pose update - x={x:.3f}, y={y:.3f}, h={h:.2f}")
        socketio.emit("pose", payload)
        return True
    
    
class base(baseprocess): 
    pass

ROUTE_DIR = "routes"

def rx_commands(filename):
    #open file and fill commands
    commands.clear()
    filepath = os.path.join(ROUTE_DIR, filename)
    route_payload = {"id": str(uuid.uuid4()), "route": []}
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            route_payload["route"].append({
                "distance": float(row["distance"]),
                "angle": float(row["angle"]),
            })                                                                                                                          

    commands.append(route_payload)
    p.send_event(src=orover.controller.remote_interface,
                 reason=orover.cmd.moveRoute,
                    body=commands[0])



###########################################################################
# Web server
###########################################################################

# Read config and create Flask/SocketIO BEFORE starting the ZMQ listener thread
# so that handlers can safely reference 'socketio' as soon as messages arrive.
config, _ = orover.readConfig(name_requested=True)


_script = os.path.basename(sys.argv[0])
_app_name = next((name for name, path in config.items("scripts") if _script == os.path.basename(path.strip())), os.path.splitext(_script)[0]) if config.has_section("scripts") else os.path.splitext(_script)[0]

app = Flask(_app_name
           ,static_folder   = config.get("app","static_folder",   fallback="static")
           ,template_folder = config.get("app", "template_folder", fallback="template"))
app.config['debug'] = config.getboolean("app","debug", fallback=True)
app.config['host'] =  config.get("app","host", fallback="localhost")
app.config['port'] = config.getint("app","port", fallback=5000)
app.config['SECRET_KEY'] = config.get("app","secret_key", fallback="default_secret_key")

commands = []  # globals
socketio = SocketIO(app, cors_allowed_origins="*")

# Now start the base process (which launches the ZMQ listener thread); socketio is defined above.
p = base(handler=handler(),threadingsubsocket=True)  # WITH threading enabled for ZMQ listener

# ---------------------------
# / route -> frontend sends messages to BOSS
# ---------------------------
@app.route("/")
def index():
    hb_interval = config.getint("orover", "heartbeat_interval", fallback=20)
    return render_template("index.html", heartbeat_interval=hb_interval)

# ---------------------------
# /grid route -> frontend sends messages to BOSS
# ---------------------------
@app.route("/grid")
def grid_view():
    return render_template("grid.html")

# ---------------------------
# /grid-data -> frontend sends messages to BOSS
# ---------------------------
@app.route("/grid-data")
def grid_data():
    # Return the current grid and robot state as JSON for the frontend to render.
    return jsonify({
        "map": shared_state.get("map", {}),
        "robot": shared_state.get("robot", {}),
    })


# ---------------------------
# /publish route -> frontend sends messages to BOSS
# ---------------------------
@app.route("/publish", methods=["POST"])
def publish():

    data = request.json
    message = data.get("message")
    p.logger.debug(f"Received message to publish: {message}")
    pub_socket.send_string(message)

    return jsonify({"status": "sent", "message": message})

# ---------------------------
# /messages route -> frontend fetch messages
# ---------------------------
@app.route("/messages")
def get_messages():  

    messages = []

    while not message_queue.empty():
        messages.append(message_queue.get())

    return jsonify(messages)

# ---------------------------
# /control route -> frontend sends control commands to BOSS
# ---------------------------
@app.route("/control", methods=["POST"])
def control():
   
    data = request.get_json() or {}
    action = data.get("action")
    p.logger.debug(f"Received control command {action}")
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
    elif action == "stop":
        left_speed = 0.0
        right_speed = 0.0
    else:
        return {"error": f"Unknown action: {action}"}, 400

    # Send command to BOSS
    answer = p.send_event(src=orover.controller.remote_interface,
                            reason=orover.cmd.set_motor_speed,   
                            body={"left_speed": left_speed, "right_speed": right_speed})
    return jsonify({"status": answer}), 200

    # Example: small temp/voltage drift to show changes
    #state["temperature"] += 0.01
    #state["voltage"] -= 0.001

    #return jsonify({"status": "ok", "action": action, "state": state})

# ---------------------------
# /route-files route -> frontend sends messages to BOSS
# ---------------------------
@app.route("/route-files", methods=["GET"])
def route_files():
    os.makedirs(ROUTE_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(ROUTE_DIR) if f.endswith(".csv"))
    return jsonify(files=files)

# ---------------------------
# /readroute route -> frontend sends messages to BOSS
# ---------------------------
@app.route("/readroute", methods=["POST"])
def readroute():
    data = request.get_json() or {}
    filename = data.get("filename", "").strip()
    if not filename:
        return jsonify(error="No filename provided"), 400
    filepath = os.path.join(ROUTE_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify(error=f"File not found: {filename}"), 404
    rx_commands(filename)
    return jsonify(status="route processed", filename=filename)

# -----------------------------
# /route route -> frontend sends route data
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

    filename = data.get("filename", "").strip()
    if not filename:
        return jsonify(error="No filename provided"), 400

    os.makedirs(ROUTE_DIR, exist_ok=True)
    filepath = os.path.join(ROUTE_DIR, filename)

    # Save route to CSV
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["distance", "angle"])
        writer.writeheader()
        writer.writerows(route)

    return jsonify(status="route accepted", steps=len(route), filename=filename)

###########################################################################
# Main
###########################################################################

if __name__ == "__main__":
    debug_mode = config.getboolean('app', 'debug', fallback=True)
    host = config.get('app', 'host', fallback='localhost')
    port = config.getint('app', 'port', fallback=5000)

    p.logger.info(f"Starting Flask app with debug={debug_mode}, host={host}, port={port}")
    socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=False,allow_unsafe_werkzeug=True)