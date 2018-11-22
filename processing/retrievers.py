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
import pathlib
from typing import List
from typing import Optional

import pytz


class VesselDetail(object):
    id_: str
    type_: str
    timestamp: dt.datetime
    position: None

    def __init__(self, id_: str, type_: str, timestamp: dt.datetime,
                 position):
        self.id_ = id_
        self.type_ = type_
        self.timestamp = timestamp
        self.position = position


def get_vessel_positions(start: dt.datetime, end: dt.datetime,
                         region_of_interest: Optional,
                         vessel_types: List[VesselType],
                         observation_types: List[ObservationType]):
    # get settings from the admin API
    # determine which concrete importers should be used
    # call each importer sequentially
    raise NotImplementedError


def imdate_retriever(start: dt.datetime, end: dt.date,
                     region_of_interest: Optional,
                     vessel_types: List[VesselType],
                     observation_types: List[ObservationType]):
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


def csv_retriever(start, end, region_of_interest, vessel_types,
                  observation_types):
    csv_path = pathlib.Path()
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = dt.datetime.strftime("%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            if end <= ts <= start:
                pass
