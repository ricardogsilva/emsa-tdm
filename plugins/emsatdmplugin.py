"""Airflow plugin for emsa-tdm"""

from importlib import import_module
import logging
import pathlib
import sys

from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(__name__)


class EmsaTdmOperator(BaseOperator):

    @apply_defaults
    def __init__(self, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler

    def execute(self, context):
        logger.info(f"plugin context: {context}")
        logger.info(f"handler: {self.handler}")
        task_handler = lazy_import(self.handler)
        return task_handler(**context)


class EmsaTdmPlugin(AirflowPlugin):
    name = "emsa_tdm_plugin"
    operators = [
        EmsaTdmOperator,
    ]


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
    except (RuntimeError, KeyError):
        python_name = _lazy_import_python_path(path)
    return python_name


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
