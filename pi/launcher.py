#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  This script initializes and starts all configured processes
"""

import configparser
import argparse
import os
import sys
import subprocess
import signal
import time

started_processes = []
default_python_path = "python3"

# Signal handler for graceful shutdown of myself and child processes
def stop_processes(signalNumber, frame):
    global started_processes
    print('Requested to stop')

    # requesting child processes to stop
    for p in started_processes:
        print(f"Terminating process {p['name']} with PID {p['process'].pid}")   
        p["process"].terminate()
    sys.exit()


#### Main execution starts here ####


# Check if config file is given as argument, otherwise use default
parser = argparse.ArgumentParser(description="oRover startup script"
                                ,prog="python3 launcher.py")
parser.add_argument("--config"
                   ,type=str
                   ,required=False
                   ,default="config.ini"
                   ,help="Path to configuration file (default: config.ini)")  
args = parser.parse_args()
print(f"Using configuration file: {args.config}")

# Read configuration from config.ini file
config = None   
if not os.path.isfile(args.config):
    sys.exit(f"Configuration file {args.config} does not exist")

config = configparser.ConfigParser() 
config.read(args.config)

# Get python path from config file, default to "python3" if not defined
python_path = default_python_path
if config.has_option('orover', 'python_executable'):
    python_path = config.get('orover', 'python_executable').strip()
    if python_path == "":
        print(f"Python path is defined in config file but is empty, defaulting to '{default_python_path}'")
        python_path = default_python_path
else:
    print(f"Python path is not defined in config file, defaulting to '{default_python_path}'") 

# Check if processes section is defined in config file
if not config.has_section('processes'):
    sys.exit(f"{args.config} does not have a section for processes")

# Are there any processes defined in the config file?
defined_processes = config.items('processes')
if len(defined_processes) == 0:
    sys.exit(f"{args.config} does not have any processes defined in the processes section")

# Start each defined process defined in the config file, if command is empty skip the process
for p in defined_processes:
    if p[1].strip() == "":
        print(f"Process {p[0]} is defined but has no command, skipping")
        continue

    execute_command = f"{python_path} {p[1].strip()} --config={args.config}"
    print(f"Starting process {p[0]} with command: {execute_command}")

    proc = subprocess.Popen(execute_command.split())  
    started_processes.append({"name": p[0], "process": proc})
    
# All starts done, register signal handler for graceful shutdown
signal.signal(signal.SIGTERM, stop_processes)

print(f"Laucher with PID {os.getpid()} started {len(started_processes)} processes, waiting for termination signal")

# Keep the main thread alive to listen for signals
while True:
   time.sleep(1)