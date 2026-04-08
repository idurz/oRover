#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  This script initializes and starts all configured processes
"""

import os
import sys
import subprocess
import signal
import time
import oroverlib as orover
from base_process import baseprocess, handler

STOP_WAIT_SECONDS = 1.0

class handler:
    def cmd_shutdown(self,message):
        print(f"Shutdown message {message}")
        reason = message.get('body', {}).get('value', 'unknown')
        print(f"LAUNCHER: Shutdown requested, reason: {reason}")
        stop_all()
        shutdown_launcher()
        sys.exit(0)

class base(baseprocess):
    # Signal handler for graceful shutdown of myself and child processes
    def terminate(self,signalNumber, frame):
        self.ctx.term()
        self.running = False
        exit(0)


# Signal handler for graceful shutdown of myself and child processes
def stop_processes(signalNumber, frame):
    msg = f"Received termination signal {signalNumber}, stopping child processes"    
    b.logger.info(msg)
    print(msg)
    # requesting child processes to stop in reverse order of starting, to allow for dependencies to stop gracefully
    stop_all()
    shutdown_launcher()
    sys.exit(0)

# TERMINATION MESSAGES APPEAR IN LOG; START MESSAGES DONT

def stop_all():
    global started_processes

    # Phase 1: request graceful stop for all still-running children.
    for p in reversed(started_processes):
        if p["process"].poll() is None:  # Check if the process is still running
            msg = f"Terminating process {p['name']} with PID {p['process'].pid}"
            b.logger.info(msg)
            print(msg)
            p["process"].terminate()
        else:
            msg = f"Process {p['name']} with PID {p['process'].pid} is already stopped"
            b.logger.info(msg)
            print(msg)

    # Phase 2: bound waiting time and force-kill stragglers.
    deadline = time.time() + STOP_WAIT_SECONDS
    for p in reversed(started_processes):
        proc = p["process"]
        if proc.poll() is not None:
            continue

        remaining = max(0.0, deadline - time.time())
        try:
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            msg = f"Killing unresponsive process {p['name']} with PID {proc.pid}"
            b.logger.warning(msg)
            print(msg)
            proc.kill()


def shutdown_launcher():
    b.running = False

    # Avoid long linger waits while shutting down sockets/context.
    try:
        b.pub.close(0)
    except Exception:
        pass
    try:
        b.sub.close(0)
    except Exception:
        pass
    try:
        b.ctx.term()
    except Exception:
        pass


started_processes = []

# Check if all commands and events are defined in the DISPATCH dictionary of the servers
def startup_checks(config):
    # mising_dict = False
    # for c in list(orover.cmd) + list(orover.event):
    #      if not c in orover.DISPATCH:
    #         msg = f"{c.name} Not defined in DISPATCH dictionary '{c.__class__.__name__}' of the servers"
    #         b.logging.error(msg)
    #         print(msg)  
    #         mising_dict = True

    # if mising_dict:
    #     logging.error("Startup checks for DISPATCH dictionary failed, exiting") 
    #     sys.exit("Startup checks for DISPATCH dictionary failed, exiting")
        
    return


#### Main execution starts here ####
if __name__ == "__main__":
    h = handler() # Instantiate the handler class, which contains the message handlers for the BOSS server
    b = base(handler=h) # Instantiate the base class, which contains the main loop and message handling logic for the BOSS server

    startup_checks(b.config) # Do some startup checks for orover lib

    # Get python path from config file, default to "python3" if not defined
    if b.config.has_option("orover", "python_exec"):
        python_path = b.config.get("orover", "python_exec", fallback="python3")
    else:
        b.logger.warning(f"Python path is not defined in config file, defaulting to 'python3'") 
        python_path = "python3"

    # Check if scipts section is defined in config file
    if not b.config.has_section('scripts'):
        sys.exit(f"config does not have a section [scripts] with defined processes")

    # Are there any processes defined in the config file?
    defined_processes = b.config.items('scripts')
    if len(defined_processes) == 0:
        sys.exit(f"config does not have any processes defined in the [scripts] section")
    
    b.logger.info(f"-------------------- Starting o R o v e r --------------------")
    print(f"-------------------- Starting o R o v e r --------------------")

    # Start each defined process defined in the config file, if command is empty skip the process
    for p in defined_processes:
        if p[1].strip() == "":
            b.logger.warning(f"Process {p[0]} is defined but has no command, skipping")
            continue

        execute_command = f"{python_path} {p[1]} --config={b.configfile}"
        b.logger.info(f"Starting process {p[0]} with command: {execute_command}")

        proc = subprocess.Popen(execute_command.split())  
        started_processes.append({"name": p[0], "process": proc})
        time.sleep(1) # Give the process some time to start before starting the next one
      
    # All starts done, register signal handler for graceful shutdown
    signal.signal(signal.SIGTERM, stop_processes)

    m = f"Laucher with PID {os.getpid()} started {len(started_processes)} processes, waiting for termination signal"
    print(m)
    b.logger.info(m)
    b.logger.info(f"-------------------- Started o R o v e r --------------------")
    print(f"-------------------- Started o R o v e r --------------------")

    b.run() # Start the main loop of the server, which will listen for messages and call the appropriate handlers based on the message reason

# Keep the main thread alive to listen for signals
#while True:
#   time.sleep(1)