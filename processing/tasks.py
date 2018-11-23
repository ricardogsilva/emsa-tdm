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

from collections import OrderedDict
import datetime as dt
import logging
import pathlib

import fiona
from fiona.crs import from_epsg
import shapely.wkt

from . import utils
from .tiles import build_grid

logger = logging.getLogger(__name__)


def get_data_retriever(template_env, template_class_path, airflow_home):
    template = template_env.from_string(template_class_path)
    class_path = template.render(airflow_home=airflow_home)
    return utils.lazy_import(class_path)


def retrieve_data(execution_date, params, dag, conf, **kwargs):
    vessel = params.get("vessel")
    settings = utils.get_settings()  # async task re-asserts the world
    vessel_settings = utils.get_vessel_settings(settings, vessel)
    sensor_settings = utils.get_sensor_settings(settings, params["sensor"])
    retriever = get_data_retriever(
        dag.get_template_env(),
        settings["retriever"],
        conf.AIRFLOW_HOME
    )
    start = dt.datetime(
        execution_date.year, execution_date.month, execution_date.day,
        tzinfo=dt.timezone.utc
    )
    tile = _get_current_tile(params["tile"], settings)
    # FIXME: enlarge tile
    retriever_generator = retriever(
        start=start,
        end=start+dt.timedelta(hours=24),
        region_of_interest=tile,
        vessel_types_mapping=vessel_settings["retriever_attribute_mapping"],
        sensor_type_mapping=sensor_settings["retriever_attribute_mapping"]
    )
    for vessel_position in retriever_generator:
        mmsi, ts, point = vessel_position
        vessel_detail = utils.VesselDetail(
            id_=mmsi, type_=vessel, timestamp=ts, position=point)
        print(f"vessel_detail: {vessel_detail.id_} {vessel_detail.position.wkt}")
    # save retrieved data somewhere
    # destination_path = pathlib.Path(
    #     f"~/data/retrieved/{execution_date.strftime('Y%m%d%')}/"
    #     f"tile_{params['tile']:03d}/{vessel}.gpkg"
    # )
    # destination_path.parent.mkdir(parents=True, exist_ok=True)
    # with fiona.open(
    #         str(destination_path),
    #         "w",
    #         driver="GPKG",
    #         crs=from_epsg(3035),
    #         schema={
    #             "geometry": "Point",
    #             "properties": OrderedDict([
    #                 ("mmsi", "int"),
    #                 ("vessel_type", "str"),
    #                 ("timestamp", "str"),
    #             ])
    #         }
    # )


def pre_process_data(**context):
    logger.info("hi, this is the pre_process_data task")


def aggregator(**context):
    logger.info("hi, this is the aggregator task")


def _get_current_tile(tile_number, settings):
    grid = build_grid(
        shapely.wkt.loads(settings["region_of_interest"]),
        num_tiles=settings["processing_tiles"]
    )
    cell_polygon = grid[tile_number][0]
    return cell_polygon
