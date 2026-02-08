#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  #####    RRRRRR     ######    V     V   EEEEEEE   RRRRRR
    #     #   R     R   #      #   V     V   E         R     R
    #     #   R     R   #      #    V   V    E         R     R
    #     #   RRRRRR    #      #    V   V    EEEEE     RRRRRR
    #     #   R   R     #      #     VV      E         R   R
     #####    R    R     ######      VV      EEEEEEE   R    R  

   License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
   Description: The BOSS server for the ROVER. This file contains the 
                handlers for boss."""
import orover_lib as orover

#class handler:
#""" Contains the handlers for BOSS messages """


def event_object_detected(message):
    """ Handler for object detected events
        Parameters:
            message:   The standard message dictionary
                body of message shoud contain parameter 'distance' 
                with distance in cm (float)
        Returns:
            on error string with error description
            on success string "OK" 
    """
    sensor = orover.get_name(message.get('src'))
    body = message.get('body', {})
    if not "distance" in body:
        return f"message {message['id']} received without distance parameter in body"
   
    d = body.get('distance',0)
    # dummy action: print warning if object too close
    print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
    return "OK"


def cmd_shutdown(socket,message,context, logger):
    """ Handler for shutdown command
        Parameters:
                socket:    The ZMQ socket to send reply to
                message:   The standard message dictionary
                    body of message may contain parameter 'value'
                    with reason for shutdown (string). If not present,
                    reason is 'unknown'
                context:   The ZMQ context to terminate
                logger:    The logger to log shutdown message
            Returns:
                This handler does not return, it shuts down the server
                However it sends an "OK" reply before shutting down
        """
    print(f"Shutdown message {message}")
    reason = message.get('body', {}).get('value', 'unknown')
    print(f"BOSS: Shutdown requested, reason: {reason}")
    socket.send(b"OK")
    socket.close(linger=2500)
    context.term()
    logger.info('Finished')
    exit(0)

def toactuar_motor_wheels(message):
    """ Handler for object detected events
        Parameters:
            ser: serial port
            left_speed: left wheel speed
            right_speed: right wheel speedS
        Returns:
            on error string with error description
            on success string "OK" 
    """
    sensor = orover.get_name(message.get('src'))
    print(f"BOSS: in actuator_motor wheels {sensor}")
    body = message.get('body', {})
    if not "left_speed" in body:
        return f"message {message['id']} received without left_speed parameter in body"
  
    return "OK"