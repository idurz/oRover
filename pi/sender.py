import zmq
import time

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5555")

# VERY IMPORTANT: allow subscribers time to connect
time.sleep(1)

while True:
    a = "topic string"
    pub.send_string(a)
    print(f"DEBUG sender: {a}")
    time.sleep(1)
