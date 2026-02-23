#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  This script initializes and starts all configured processes
"""

import logging
import os
import sys
import subprocess
import signal
import time
import oroverlib as orover
from base_process import baseprocess


started_processes = []

class base(baseprocess):
    # Signal handler for graceful shutdown of myself and child processes
    def terminate(self,signalNumber, frame):
        #self.pub.close()
        #self.sub.close()
        self.ctx.term()
        self.running = False
        sys.exit()


# Signal handler for graceful shutdown of myself and child processes
def stop_processes(signalNumber, frame):
    global started_processes
    logging.info(f"Received termination signal {signalNumber}, stopping child processes")
    print(f"Received termination signal {signalNumber}, stopping child processes")
    
    # requesting child processes to stop in reverse order of starting, to allow for dependencies to stop gracefully
    for p in reversed(started_processes):
        logging.info(f"Terminating process {p['name']} with PID {p['process'].pid}")   
        print(f"Terminating process {p['name']} with PID {p['process'].pid}")
        p["process"].terminate()
    sys.exit()

# TERMINATION MESSAGES APPEAR IN LOG; START MESSAGES DONT

# Check if all commands and events are defined in the DISPATCH dictionary of the servers
def startup_checks(config):
    mising_dict = False
    for c in list(orover.cmd) + list(orover.event):
         if not c in orover.DISPATCH:
            msg = f"{c.name} Not defined in DISPATCH dictionary '{c.__class__.__name__}' of the servers"
            b.logging.error(msg)
            print(msg)  
            mising_dict = True

    if mising_dict:
        logging.error("Startup checks for DISPATCH dictionary failed, exiting") 
        sys.exit("Startup checks for DISPATCH dictionary failed, exiting")
        
    return


#### Main execution starts here ####
b = base()  
startup_checks(b.config) # Do some startup checks for orover lib

# Get python path from config file, default to "python3" if not defined
if b.config.has_option("orover", "python_exec"):
    python_path = b.config.get("orover", "python_exec", fallback="python3")
else:
    logging.warning(f"Python path is not defined in config file, defaulting to 'python3'") 
    python_path = "python3"

# Check if scipts section is defined in config file
if not b.config.has_section('scripts'):
    sys.exit(f"config does not have a section [scripts] with defined processes")

# Are there any processes defined in the config file?
defined_processes = b.config.items('scripts')
if len(defined_processes) == 0:
    sys.exit(f"config does not have any processes defined in the [scripts] section")

logging.info(f"-------------------- Starting o R o v e r --------------------")
print(f"-------------------- Starting o R o v e r --------------------")

# Start each defined process defined in the config file, if command is empty skip the process
for p in defined_processes:
    if p[1].strip() == "":
        logging.warning(f"Process {p[0]} is defined but has no command, skipping")
        continue

    execute_command = f"{python_path} {p[1]} --config={b.configfile}"
    logging.info(f"Starting process {p[0]} with command: {execute_command}")

    proc = subprocess.Popen(execute_command.split())  
    started_processes.append({"name": p[0], "process": proc})
    
# All starts done, register signal handler for graceful shutdown
signal.signal(signal.SIGTERM, stop_processes)

print(f"Laucher with PID {os.getpid()} started {len(started_processes)} processes, waiting for termination signal")

# Keep the main thread alive to listen for signals
while True:
   time.sleep(1)