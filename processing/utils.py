#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

"""utility functions for processing code"""

import json
import logging
import pathlib

from airflow import configuration

logger = logging.getLogger(__name__)


def get_settings():
    home = configuration.get("core", "airflow_home")
    settings_path = pathlib.Path(home) / "tests/data/test-settings.json"
    with settings_path.open() as fh:
        return json.load(fh)
