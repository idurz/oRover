#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
    #     #   R     R   #      #   V     V   E         R     R
    #     #   R     R   #      #    V   V    E         R     R
    #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
    #     #   R   R     #      #     VV      E         R   R
     #####    R    R     ######      VV      EEEEEEE   R    R  

   License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
   Description: Manual gracefull shutdown of the BOSS server"""

import zmq # pyright: ignore[reportMissingImports]
import orover_lib as orover
#import json, uuid, os
from datetime import datetime

def main():

    print("Requesting BOSS to stop")
    socket = orover.connect_to_server()

    answer = orover.send(socket
               ,src=orover.controller.remote_interface
               ,type=orover.cmd.shutdown
               ,body={"value": "maintenance"})
    if answer:
        print(f"Boss told me {answer}")

    orover.disconnect_from_server(socket)

if __name__ == "__main__":
    main()
