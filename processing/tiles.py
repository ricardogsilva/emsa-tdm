#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

"""Utilities for calculating processing tiles

Example usage:

Lets imagine our region of interest starts at coordinates (20, 30) and has an
extent of 100 000 sq km

>>> extent = (100000000, 100000000)
>>> for tile in build_grid(*extent, start_x=20, start_y=30):
...     print(get_tile_extents(tile))

"""

import math

import sympy


def find_tile_dimensions(area, num_tiles):
    tile_area = math.ceil(area) / num_tiles
    divisors = sympy.divisors(tile_area)
    num_divisors = len(divisors)
    half = int(num_divisors / 2)
    if num_divisors % 2 == 0:  # number of divisors is even
        result = divisors[half-1:half+1]
    else:  # number of divisors is odd
        result = [divisors[half]] * 2
    return result


def build_grid(width, height, num_tiles, start_x=0, start_y=0):
    area = math.ceil(width * height)
    tile_width, tile_height = find_tile_dimensions(area, num_tiles)
    result = []
    current_width = 0
    current_height = 0
    for tile in range(num_tiles):
        current_x = start_x + current_width
        current_y = start_y + current_height
        next_x = current_x + tile_width
        next_y = current_y + tile_height
        p1 = (current_x, current_y)
        p2 = (next_x, current_y)
        p3 = (next_x, next_y)
        p4= (current_x, next_y)
        result.append((p1, p2, p3, p4))
        current_width += tile_width
        if current_width + tile_width > width:
            current_width = 0
            current_height += tile_height
    return result


def get_tile_extents(tile):
    min_x = tile[0][0]
    max_x = tile[2][0]
    min_y = tile[0][1]
    max_y = tile[3][1]
    return min_x, min_y, max_x, max_y
