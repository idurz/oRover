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
import fcntl
import atexit
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
    except (AttributeError):
        pass
    try:
        b.sub.close(0)
    except (AttributeError):
        pass
    try:
        b.ctx.term()
    except (AttributeError):
        pass


started_processes = []
_launcher_lock_fd = None


def _release_launcher_lock():
    global _launcher_lock_fd
    if _launcher_lock_fd is None:
        return
    try:
        fcntl.flock(_launcher_lock_fd, fcntl.LOCK_UN)
    except OSError:
        pass
    try:
        os.close(_launcher_lock_fd)
    except OSError:
        pass
    _launcher_lock_fd = None


def _acquire_launcher_lock():
    """Acquire exclusive launcher lock; return (ok, existing_pid)."""
    global _launcher_lock_fd
    lockfile = "/tmp/orover_launcher.lock"

    fd = os.open(lockfile, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        existing_pid = "unknown"
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            data = os.read(fd, 64).decode().strip()
            if data:
                existing_pid = data
        except OSError:
            pass
        os.close(fd)
        return False, existing_pid

    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode())
    _launcher_lock_fd = fd
    atexit.register(_release_launcher_lock)
    return True, None


#### Main execution starts here ####
if __name__ == "__main__":
    lock_ok, existing_pid = _acquire_launcher_lock()
    if not lock_ok:
        print(
            "Another launcher instance is already running "
            f"(PID: {existing_pid}). "
            "Not starting a second launcher."
        )
        sys.exit(1)

    h = handler() # Instantiate the handler class, which contains the message handlers for the BOSS server
    b = base(handler=h) # Instantiate the base class, which contains the main loop and message handling logic for the BOSS server

    #startup_checks(b.config) # Do some startup checks for orover lib

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
    
    msg = f"-------------------- Starting o R o v e r --------------------"
    b.logger.info(msg)
    print(msg)

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
    msg = f"-------------------- Started o R o v e r --------------------"
    b.logger.info(msg)
    print(msg)

    b.run() # Start the main loop of the server, which will listen for messages and call the appropriate handlers based on the message reason