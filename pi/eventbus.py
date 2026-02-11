#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  zmq event bus for oRover processes to publish events to each other and the BOSS
"""
import zmq

# from base_process import BaseProcess

# class Eventbus(BaseProcess):
#     def loop(self):
#         while True:
#             msg = self.sub.recv_json()
#             print(f"Eventbus message received {msg}")
#             self.logger.info("Eventbus message received", extra = {"message" : msg})
#             self.pub.send_json(msg)

# if __name__ == "__main__":
#     p = Eventbus()
#     p.loop()


ctx = zmq.Context()
xsub = ctx.socket(zmq.XSUB)
xsub.bind("tcp://*:5556")

xpub = ctx.socket(zmq.XPUB)
xpub.bind("tcp://*:5555")

print("Event bus running:")
print("  publishers -> tcp://*:5556")
print("  subscribers -> tcp://*:5555")

zmq.proxy(xsub, xpub)