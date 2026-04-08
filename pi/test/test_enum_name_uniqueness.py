#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Fail if enum member names are duplicated across oRover enum classes.

Duplicate names (for example: "shutdown") can cause ambiguous lookups in
generic name->enum conversion logic and lead to wrong handler registration.
"""

from __future__ import annotations

import inspect
import os
import sys
from collections import defaultdict
from enum import IntEnum

# Ensure pi/ is on sys.path when running this script from pi/test.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PI_DIR = os.path.dirname(SCRIPT_DIR)
if PI_DIR not in sys.path:
    sys.path.insert(0, PI_DIR)

import oroverlib as orover


def iter_orover_enums():
    """Yield IntEnum classes defined in oroverlib."""
    for _, obj in inspect.getmembers(orover, inspect.isclass):
        if obj.__module__ == orover.__name__ and issubclass(obj, IntEnum):
            yield obj


def find_duplicate_member_names():
    """Return a mapping: member_name -> [EnumClassNames...] for duplicates."""
    owners = defaultdict(list)

    for enum_cls in iter_orover_enums():
        for member_name in enum_cls.__members__:
            owners[member_name].append(enum_cls.__name__)

    return {
        member_name: sorted(class_names)
        for member_name, class_names in owners.items()
        if len(class_names) > 1
    }


def main() -> int:
    duplicates = find_duplicate_member_names()

    if not duplicates:
        print("PASS: no duplicate enum member names found across oroverlib enums")
        return 0

    print("FAIL: duplicate enum member names detected")
    for member_name, class_names in sorted(duplicates.items()):
        print(f"  - {member_name}: {', '.join(class_names)}")

    print("Hint: make member names unique across enum classes or use typed lookup logic.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())