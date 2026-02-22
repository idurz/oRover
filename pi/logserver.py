#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Socketserver for logging
"""

import pickle
import logging
import logging.handlers
import socketserver
import struct
import oroverlib as orover
#import setproctitle
from base_process import baseprocess

class base(baseprocess):
    def create_pub_socket(self, ctx):
        return None # No pub socket needed for logserver, we only receive logs via the socket handler
    
    def create_sub_socket(self, ctx):
        return None # No sub socket needed for logserver, we only receive logs via the socket handler, we don't subscribe t
    
    

# This is based on the Python 3.11 standard library example for a socket-based logging receiver.
class LogRecordStreamHandler(socketserver.StreamRequestHandler):

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)


    def unPickle(self, data):
        return pickle.loads(data)


     # if a name is specified, we use the named logger rather than the one implied by the record.
    def handleLogRecord(self, record):
       
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # EVERY record received gets logged. 
        logger.handle(record)


# This is a simple TCP socket-based logging receiver suitable for testing.
class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


#### Main execution starts here ####
def main():
    b =base() # Create an instance of the base class to get config and logger

    config  = orover.readConfig()
    #setproctitle.setproctitle(f"orover:{orover.getmodulename(config)}")

    logformat = b.config.get("orover", "logformat", raw=True, fallback="%(asctime)s %(name)-15s %(levelname)-8s %(message)s")
    datefmt   = b.config.get("orover", "logdatefmt", raw=True, fallback="%Y-%m-%d %H:%M:%S")
    filename  = b.config.get("orover", "logfile",    fallback="logserver.log")

    logging.basicConfig(format=logformat, datefmt=datefmt, filename=filename)

    tcpserver = LogRecordSocketReceiver()
    tcpserver.serve_until_stopped()


if __name__ == '__main__':
    main()