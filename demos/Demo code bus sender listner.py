Demo code bus,sender, listner

##### bus
import zmq

ctx = zmq.Context()
xsub = ctx.socket(zmq.XSUB)
xsub.bind("tcp://*:5556")

xpub = ctx.socket(zmq.XPUB)
xpub.bind("tcp://*:5555")

print("Event bus running:")
print("  publishers -> tcp://*:5556")
print("  subscribers -> tcp://*:5555")

zmq.proxy(xsub, xpub)


#### SENDER

import zmq
import time

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5556")

# VERY IMPORTANT: allow subscribers time to connect
time.sleep(1)
i = 0
while True:
    i = i + 1
    a = f"topic twee{i}"
    pub.send_string(a)
    print(f"DEBUG sender twee: {a}")
    time.sleep(0.01)


#### LISTNER
import zmq

ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://localhost:5555")
sock.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    msg = sock.recv_string()
    print(f"DEBUG receiver: {msg}")
