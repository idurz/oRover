#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  Navigation grid encoding and decoding
"""

from math import isfinite


def encode_grid(cells, resolution_m, origin_cell):
    if not isinstance(cells, list) or not cells or not isinstance(cells[0], list) or not cells[0]:
        raise ValueError("grid must be a non-empty rectangular list")

    height = len(cells)
    width = len(cells[0])
    if any(not isinstance(row, list) or len(row) != width for row in cells):
        raise ValueError("grid rows must have equal width")

    sparse_cells = []
    for row_index, row in enumerate(cells):
        for column_index, value in enumerate(row):
            numeric_value = float(value)
            if not isfinite(numeric_value):
                raise ValueError("grid values must be finite")
            scaled_value = round(numeric_value * 100)
            if scaled_value:
                sparse_cells.append([row_index * width + column_index, scaled_value])

    resolution_m = float(resolution_m)
    if not isfinite(resolution_m) or resolution_m <= 0:
        raise ValueError("grid resolution must be finite and positive")

    return {
        "width": width,
        "height": height,
        "cells": sparse_cells,
        "resolution_m": resolution_m,
        "origin_cell": int(origin_cell),
    }


def decode_grid(payload):
    if not isinstance(payload, dict):
        raise ValueError("grid payload must be an object")

    width = payload.get("width")
    height = payload.get("height")
    cells = payload.get("cells")
    if type(width) is not int or type(height) is not int or width < 1 or height < 1:
        raise ValueError("grid dimensions must be positive integers")
    if width * height > 1_000_000:
        raise ValueError("grid dimensions are too large")
    if not isinstance(cells, list):
        raise ValueError("grid cells must be a list")

    grid = [[0.0] * width for _ in range(height)]
    for cell in cells:
        if not isinstance(cell, list) or len(cell) != 2:
            raise ValueError("grid cells must be [index, value] pairs")
        index, value = cell
        if type(index) is not int or type(value) is not int or not 0 <= index < width * height:
            raise ValueError("grid cell index or value is invalid")
        grid[index // width][index % width] = value / 100.0

    resolution_m = float(payload.get("resolution_m"))
    origin_cell = payload.get("origin_cell")
    if not isfinite(resolution_m) or resolution_m <= 0:
        raise ValueError("grid resolution must be finite and positive")
    if type(origin_cell) is not int:
        raise ValueError("grid origin must be an integer")

    return grid, resolution_m, origin_cell