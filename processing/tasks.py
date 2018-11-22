#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

"""airflow tasks"""

import logging

import shapely.wkt

from .utils import get_settings
from .tiles import build_grid

logger = logging.getLogger(__name__)


def retrieve_data(yesterday_ds, params, **context):
    logger.info(f"context: {context}")
    logger.info(f"yesterday_ds: {yesterday_ds}")
    sensor = params.get("sensor")
    tile_number = params.get("tile")
    vessel = params.get("vessel")
    settings = get_settings()  # async task re-asserts the world
    vessel_settings = [
        i for i in settings["vessels"] if i["name"] == vessel][0]
    data_retriever_template = vessel_settings["retriever"]
    # get data retriever code
    # parametrize it with correct start, end, extent, etc
    start = None
    end = None
    ship_types = None  # convert between vessel name and DB column values
    sensor_type = None  # convert between sensor name and DB column values
    tile = _get_current_tile(tile_number, settings)
    logger.info(f"cell: {tile.wkt}")
    # call retriever
    # save retrieved data somewhere


def pre_process_data(**context):
    logger.info("hi, this is the pre_process_data task")


def aggregator(**context):
    logger.info("hi, this is the aggregator task")


def _get_current_tile(tile_number, settings):
    grid = build_grid(
        shapely.wkt.loads(settings["region_of_interest"]["bbox_wkt"]),
        num_tiles=settings["processing_tiles"]
    )
    cell = grid[tile_number]
    return cell
