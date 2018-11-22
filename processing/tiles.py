#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

"""Utilities for calculating processing tiles"""

from itertools import product
import logging
import math

from shapely.geometry import Polygon

logger = logging.getLogger(__name__)


def build_grid(region_of_interest: Polygon, num_tiles:int):
    min_x, min_y, max_x, max_y = region_of_interest.bounds
    width = max_x - min_x
    height = max_y - min_y
    start_x = min_x
    start_y = min_y
    num_tiles = adjust_num_tiles(num_tiles)
    num_rows = int(math.sqrt(num_tiles))
    num_cols = num_rows
    tile_width = math.ceil(width / num_cols)
    tile_height = math.ceil(height / num_rows)
    result = []
    for row, column in product(range(num_rows), range(num_cols)):
        current_x = start_x + tile_width * row
        current_y = start_y + tile_height * column
        next_x = current_x + tile_width
        next_y = current_y + tile_height
        p1 = (current_x, current_y)
        p2 = (next_x, current_y)
        p3 = (next_x, next_y)
        p4 = (current_x, next_y)
        result.append(Polygon((p1, p2, p3, p4, p1)))
    return result


def adjust_num_tiles(num_tiles):
    """Enlarge input ``num_tiles`` so that it is a perfect square"""
    root = math.sqrt(num_tiles)
    if root % 1 != 0:
        logger.debug("Augmenting num_tiles...")
        result = math.pow(math.ceil(root), 2)
    else:
        result = num_tiles
    return int(result)
