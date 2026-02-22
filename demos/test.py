#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r -> object recognition and versatile exploration robot
     License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description: Allow testing of the BOSS server with command-line tool
"""
import oroverlib as orover
import logging,logging.handlers
import os
import sys
import subprocess
import time

# Do some startup checks for orover lib

def startup_check_dict_in_def(config):
    # Check if all defined in Dispatch are defined as function in the handler class of the servers, to avoid 
    # starting the server and then exiting with an error due to a missing function in the handler class
    missing_func = False
    for c in orover.DISPATCH:
        func_name = orover.DISPATCH[c].__name__
        if not hasattr(orover.handler, func_name):
            msg = f"{func_name} Not defined as function in the handler class of the servers"
            logging.error(msg)
            print(msg)  
            missing_func = True 

    if missing_func:
        logging.error("Startup checks for handler functions failed, exiting") 
        sys.exit("Startup checks for handler functions failed, exiting")


def startup_check_classes_in_dict(config):

    # Check if all commands and events are defined in the DISPATCH dictionary of the servers
    mising_dict = False
    for c in list(orover.cmd) + list(orover.event):
         if not c in orover.DISPATCH:
            msg = f"{c.name} Not defined in DISPATCH dictionary '{c.__class__.__name__}' of the servers"
            logging.error(msg)
            print(msg)  
            mising_dict = True

    if mising_dict:
        logging.error("Startup checks for DISPATCH dictionary failed, exiting") 
        sys.exit("Startup checks for DISPATCH dictionary failed, exiting")
    return



#### Main execution starts here ####
config, configfile = orover.readConfig(True)
logger = orover.setlogger(config)

#setproctitle.setproctitle(f"orover:{orover.getmodulename(config)}")

# Do some startup checks for orover lib
startup_check_classes_in_dict(config)
startup_check_dict_in_def(config)

# 
#, python path and defined processes before starting any process, to avoid starting some processes and then exiting with an error due to a missing config or python path
# Get python path from config file, default to "python3" if not defined
if config.has_option("orover", "python_exec"):
    python_path = config.get("orover", "python_exec", fallback="python3")
else:
    logging.warning(f"Python path is not defined in config file, defaulting to 'python3'") 
    python_path = "python3"

# Check if scipts section is defined in config file
if not config.has_section('scripts'):
    sys.exit(f"config does not have a section [scripts] with defined processes")

# Are there any processes defined in the config file?
defined_processes = config.items('scripts')
if len(defined_processes) == 0:
    sys.exit(f"config does not have any processes defined in the [scripts] section")

print(f"Config check ok")