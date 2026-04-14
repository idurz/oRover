from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import oroverlib as orover
import threading
import csv
from base_process import baseprocess, handler

heartbeats = {};
state = {"temperature": 22,
        "speed": 13,
        "angle": 0,
        "voltage": 14}

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

    def event_heartbeat(self, msg):
    
        global heartbeats
        # event.heartbeat {"id": "2d2dbb81-64f8-46bd-9585-2b64280af9a2", "ts": "2026-03-14T19:55:52.527138", "src": 1000, 
        # "me": "eventbus", "host": "robot", "prio": 5, "reason": 6402, "body": {"script": "eventbus"}}

        if "me" in msg and "ts" in msg:
           # store name and timestamp of last heartbeat for each script
           heartbeats[msg["me"]] = msg["ts"]
           p.logger.debug(f"Stored heartbeat from {msg['me']}")
           socketio.emit("heartbeat", {"me": msg["me"], "timestamp": msg["ts"]})
        return True
    
    def state_battery(self, msg):
        # Example handler for battery state messages, expects body to contain "voltage" field
        voltage = msg.get("body", {}).get("voltage")
        if voltage is not None:
            p.logger.info(f"Battery voltage: {voltage} V")
            socketio.emit("battery_state", {"voltage": voltage})
            return True
        else:
            p.logger.warning("Received battery state message without voltage field")
            return False
        
    def state_imu(self, msg):
        # Example handler for IMU state messages, expects body to contain "heading", "pitch", and "roll" fields
        heading = msg.get("body", {}).get("heading")
        pitch = msg.get("body", {}).get("pitch")
        roll = msg.get("body", {}).get("roll")
        if heading is not None and pitch is not None and roll is not None:
            p.logger.info(f"IMU data - Heading: {heading} deg, Pitch: {pitch} deg, Roll: {roll} deg")
            socketio.emit("imu_state", {"heading": heading, "pitch": pitch, "roll": roll})
            return True
        else:
            p.logger.warning("Received IMU state message without required fields")
            return False
    
    
class base(baseprocess):
    pass



def rx_commands():
    # Placeholder for future command execution from CSV
    print("Done.")


###########################################################################
# Web server
###########################################################################

# Read config and create Flask/SocketIO BEFORE starting the ZMQ listener thread
# so that handlers can safely reference 'socketio' as soon as messages arrive.
config, _ = orover.readConfig(name_requested=True)

import os as _os, sys as _sys
_script = _os.path.basename(_sys.argv[0])
_app_name = next((name for name, path in config.items("scripts") if _script == _os.path.basename(path.strip())), _os.path.splitext(_script)[0]) if config.has_section("scripts") else _os.path.splitext(_script)[0]

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

@app.route("/")
def index():
    hb_interval = config.getint("orover", "heartbeat_interval", fallback=20)
    return render_template("index.html", heartbeat_interval=hb_interval)


# ---------------------------
# EXAMPLE HTTP route -> publish ZMQ
# ---------------------------
@app.route("/publish", methods=["POST"])
def publish():

    data = request.json
    message = data.get("message")
    p.logger.debug(f"Received message to publish: {message}")
    pub_socket.send_string(message)

    return jsonify({"status": "sent", "message": message})


# ---------------------------
# EXAMPLE HTTP route -> frontend fetch messages
# ---------------------------
@app.route("/messages")
def get_messages():  

    messages = []

    while not message_queue.empty():
        messages.append(message_queue.get())

    return jsonify(messages)


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

    #if answer:
    #    print(f"Boss told me {answer}")

    return jsonify({"status": answer}), 200

    # Example: small temp/voltage drift to show changes
    #state["temperature"] += 0.01
    #state["voltage"] -= 0.001

    #return jsonify({"status": "ok", "action": action, "state": state})


#@app.route("/status")
#def status():
#    global state
    # Return current values for frontend to display
    #return jsonify({
    #    "temperature": round(state["temperature"], 2),
    #    "speed": round(state["speed"], 2),
    #    "angle": round(state["angle"], 2),
    #    "voltage": round(state["voltage"], 2)
    #})
#    return {}

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
    debug_mode = config.getboolean('app', 'debug', fallback=True)
    host = config.get('app', 'host', fallback='localhost')
    port = config.getint('app', 'port', fallback=5000)

    p.logger.info(f"Starting Flask app with debug={debug_mode}, host={host}, port={port}")
    socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=False,allow_unsafe_werkzeug=True)

    #app.run(debug=True,host="0.0.0.0",port=5000)