import oroverlib as orover
import time
from base_process import baseprocess

class sender(baseprocess):
    self.myname = "test_sender"


ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5555")

# VERY IMPORTANT: allow subscribers time to connect
time.sleep(1)

while True:
    p = sender()
    p.logger.info("Sending test message")
    p.send_event(orover.origin.test_message, orover.event.test_message, {"data": "Hello, World!"})
    time.sleep(10)
