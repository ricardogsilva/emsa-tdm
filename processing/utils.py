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

import datetime as dt
from importlib import import_module
import json
import logging
import pathlib
from shapely import geometry
import sys

from airflow import configuration

logger = logging.getLogger(__name__)


class VesselDetail(object):
    id_: str
    type_: str
    timestamp: dt.datetime
    position: geometry.Point

    def __init__(self, id_: str, type_: str, timestamp: dt.datetime,
                 position: geometry.Point):
        self.id_ = id_
        self.type_ = type_
        self.timestamp = timestamp
        self.position = position




def get_settings():
    home = configuration.get("core", "airflow_home")
    settings_path = pathlib.Path(home) / "tests/data/test-settings.json"
    with settings_path.open() as fh:
        return json.load(fh)


def get_vessel_settings(settings, name):
    return _get_list_object_settings(settings, "vessels", name)


def get_sensor_settings(settings, name):
    return _get_list_object_settings(settings, "sensor_types", name)


def _get_list_object_settings(settings, list_name, name):
    for obj in settings.get(list_name, []):
        if obj.get("name") == name:
            result = obj
            break
    else:
        result = None
    return result


def lazy_import(path: str):
    """Import a python named object dynamically.

    Parameters
    ----------
    path: str
        Path to import. It can be either a python class path or a filesystem
        path (e.g. ~/processes/callbacks.py:process_stuff)

    """

    try:
        python_name = _lazy_import_filesystem_path(path)
    except ImportError:
        python_name = _lazy_import_filesystem_path_with_python_package(path)
    except (RuntimeError, KeyError):
        python_name = _lazy_import_python_path(path)
    return python_name


def _lazy_import_filesystem_path_with_python_package(path:str):
    """Lazily import a python name from a filesystem path

    This function attempts to import the input ``path`` by assuming it is
    part of a python package. This is useful for those cases where the code
    in ``path`` uses relative imports.

    Parameters
    ----------
    path: str
        A colon separated string with the path to the module to load and the
        name of the object to import

    Returns
    -------
    The imported object

    Raises
    ------
    KeyError
        If the name is not found on the loaded python module
    RuntimeError
        If the path is not valid

    """

    filesystem_path, python_name = path.rpartition(":")[::2]
    full_path = pathlib.Path(filesystem_path).expanduser().resolve()
    if full_path.is_file():
        sys.path.append(str(full_path.parents[1]))
        loaded_module = import_module(
            f"{full_path.parent.stem}.{full_path.stem}")
        return loaded_module.__dict__.get(python_name)
    else:
        raise RuntimeError(f"Invalid path {full_path}")


def _lazy_import_filesystem_path(path: str):
    """Lazily import a python name from a filesystem path

    Parameters
    ----------
    path: str
        A colon separated string with the path to the module to load and the
        name of the object to import

    Returns
    -------
    The imported object

    Raises
    ------
    KeyError
        If the name is not found on the loaded python module
    RuntimeError
        If the path is not valid

    """

    filesystem_path, python_name = path.rpartition(":")[::2]
    full_path = pathlib.Path(filesystem_path).expanduser().resolve()
    if full_path.is_file():
        sys.path.append(str(full_path.parent))
        loaded_module = import_module(full_path.stem)
        return loaded_module.__dict__.get(python_name)
    else:
        raise RuntimeError(f"Invalid path {full_path}")


def _lazy_import_python_path(path: str):
    module_path, python_name = path.rpartition(".")[::2]
    loaded_module = import_module(module_path)
    return loaded_module.__dict__.get(python_name)
