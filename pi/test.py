#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r -> object recognition and versatile exploration robot
     License:     MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description: Allow testing of the BOSS server with command-line tool
"""
import oroverlib as orover

# Check if all commands and events are defined in the DISPATCH dictionary of the servers
# Next check if all commands and events in DISPATCH have a handler defined 

for c in (orover.cmd.__iter__(), orover.event.__iter__()):
    if not c in orover.DISPATCH: 
        print(f"{c} Not defined in DISPATCH dictionary of the servers")
