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
import os
import oroverlib as orover
from base_process import baseprocess


class base(baseprocess):
    def create_pub_socket(self, ctx):
        return None # No pub socket needed for logserver, we only receive logs via the socket handler
    
    def create_sub_socket(self, ctx):
        return None # No sub socket needed for logserver, we only receive logs via the socket handler, we don't subscribe t
    
    # Signal handler for graceful shutdown of myself and child processes
    def terminate(self,signalNumber, frame):
        self.ctx.term()
        self.running = False
        tcpserver.abort = 1
        os._exit(os.EX_OK) # sys.exit will not work here because of the socketserver, so we use os._exit to force exit immediately

    def setlogger(self,config,myname):
        pass # No need to set up a logger here, we will use the root logger for the logserver, and the socket handler will log to the appropriate logger based on the record name


class EnsureGuidFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "guid") or not record.guid:
            record.guid = "-"
        return True


def cleanup_old_logfiles(logdir, basename, max_count):
    """Keep only the last max_count log files, delete older ones"""
    import glob
    
    if not os.path.isdir(logdir):
        return
    
    # Find all log files matching the pattern: basename_YYYYMMDDHHMMSS.log
    pattern = os.path.join(logdir, f"{basename}_*.log")
    logfiles = sorted(glob.glob(pattern))
    
    # Delete old files, keep only the last max_count
    if len(logfiles) > max_count:
        for old_file in logfiles[:-max_count]:
            try:
                os.remove(old_file)
                print(f"Removed old logfile: {old_file}")
            except OSError as e:
                print(f"Failed to remove {old_file}: {e}")

    
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
if __name__ == '__main__':

    b = base() # Create an instance of the base class to get config and logger

    logdir = b.config.get("orover", "logdir", fallback="logs")
    logformat = b.config.get("orover", "logformat", raw=True, fallback="%(asctime)s %(name)-15s %(levelname)-8s guid=%(guid)s %(message)s")
    datefmt   = b.config.get("orover", "logdatefmt", raw=True, fallback="%Y-%m-%d %H:%M:%S")
    logfile_basename = b.config.get("orover", "logfile", fallback="orover.log")
    max_logfiles = b.config.getint("orover", "max_logfiles", fallback=10)
    
    # Create log directory if it doesn't exist
    os.makedirs(logdir, exist_ok=True)
    
    # Construct full path with timestamp
    basename = os.path.splitext(logfile_basename)[0]
    logfile = os.path.join(logdir, f"{basename}_{b.log_timestamp()}.log")
    
    logging.basicConfig(format=logformat, datefmt=datefmt, filename=logfile)
    
    # Clean up old logfiles
    cleanup_old_logfiles(logdir, basename, max_logfiles)
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(EnsureGuidFilter())

    tcpserver = LogRecordSocketReceiver()
    tcpserver.serve_until_stopped()