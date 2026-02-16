#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  The BOSS server for the ROVER. Handles messages related to 
                  object recognition and versatile exploration.
"""

import oroverlib as orover
from base_process import baseprocess

class handler:
    """ Contains the handlers for BOSS messages. Each handler takes a message as input and returns a result string. 
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

    def event_object_detected(message):
        sensor = p.enum_to_name(message.get('src'))
        body = message.get('body', {})
        if not "distance" in body:
            p.logger.warning(f"Message {message['id']} discarded from sensor {sensor}: received without distance parameter in body")
            return False
       
        d = body.get('distance',0)
        # dummy action: print warning if object too close
        print(f"BOSS: Warning: object too close to sensor {sensor} distance {d} cm")
        return True
    


    
    def cmd_shutdown(socket,message,context, logger):
        print(f"Shutdown message {message}")
        reason = message.get('body', {}).get('value', 'unknown')
        print(f"BOSS: Shutdown requested, reason: {reason}")
        socket.send(b"OK")
        socket.close(linger=2500)
        context.term()
        logger.info('Finished')
        exit(0)
    



    def cmd_set_motor_speed(message):
        source = orover.get_name(message.get('src'))
        print(f"BOSS: in actuator_motor_wheels {source}")
        body = message.get('body', {})
        if not "left_speed" in body:
            return f"message {message['id']} received without left_speed parameter in body"
      
        return
    



class boss_server(baseprocess):

    # override baseprocess methodes
    def handle_message(self, message):

        DISPATCH = {orover.event.object_detected:        handler.event_object_detected
               ,orover.cmd.shutdown:                     handler.cmd_shutdown
               ,orover.cmd.set_motor_speed:              handler.cmd_set_motor_speed
               }

        reason = message['reason']
        try:
            handler_routine = DISPATCH[reason]
        except KeyError:
            p.logger.warning(f"Message discard: {message['id']}: No handler for reason {self.enum_to_name(reason)} available in BOSS server") 
            return
       
        result = handler_routine(message)
        p.logger.debug(f"Message handled : {message}, result: {result}")
        return


    

#### Main execution starts here ####
if __name__ == "__main__":
    p = boss_server()
    p.run()