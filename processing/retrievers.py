#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

"""Ship Position Data retrievers"""

import csv
import datetime as dt
import logging
import pathlib
from typing import Optional

from pyproj import Proj
from pyproj import transform
from shapely import geometry

logger = logging.getLogger(__name__)


def imdate_retriever(start: dt.datetime, end: dt.date,
                     region_of_interest: Optional,
                     vessel_types,
                     observation_types):
    # use sqlalchemy to retrieve the data
    # - add the mappings to the query
    # - add the region of interest to the query
    query = """
    SELECT
      msid,
      timestamp,
      lat,
      lon
    FROM IMDatE.spd
    WHERE timestamp >= %(start)s
      AND timestamp <= %(end)s
    ORDER BY timestamp, msid
    """
    # for each row, create a new vessel_detail object
    raise NotImplementedError


def csv_retriever(start: dt.datetime, end: dt.datetime,
                  region_of_interest: geometry.Polygon,
                  vessel_types_mapping, sensor_type_mapping):
    in_crs = Proj(init="epsg:4326")
    out_crs = Proj(init="epsg:3035")
    ais_types = get_ais_ship_types()
    csv_path = pathlib.Path("~/data/AIS_export_201810.csv").expanduser()
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = dt.datetime.strptime(
                row["TS"][:-3],
                "%Y-%m-%d %H:%M:%S.%f"
            ).replace(tzinfo=dt.timezone.utc)
            if ts >= end:  # assumes positions are ordered by TS
                break
            elif ts < start:
                continue
            sensor_attribute_value = row.get(sensor_type_mapping["name"])
            if sensor_attribute_value != str(sensor_type_mapping["value"]):
                continue
            coords = transform(in_crs, out_crs, row["LON"], row["LAT"])
            point = geometry.Point(*coords)
            if not point.within(region_of_interest):
                continue
            mmsi = row["MMSI"]
            ship_type = ais_types.get(mmsi)
            if ship_type not in vessel_types_mapping["values"]:
                continue
            yield mmsi, ts, point


def get_ais_ship_types():
    ovr_data_path = pathlib.Path(
        "~/data/TDMS_ref_tables_sqlldr/sanitized_OVR_DATA_TABLE.csv"
    ).expanduser().resolve()
    ship_types = dict()
    with ovr_data_path.open(encoding="utf-8") as fh:
        for line in fh:
            record = line.split("|")
            mmsi = record[1]
            ais_ship_type = record[8]
            if ais_ship_type:
                ship_types[mmsi] = int(ais_ship_type)
    return ship_types

