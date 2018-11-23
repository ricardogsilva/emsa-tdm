"""Airflow plugin for emsa-tdm"""

import logging
import sys

from airflow import configuration
from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

sys.path.append(configuration.get("core", "airflow_home"))

from processing import utils

logger = logging.getLogger(__name__)


class EmsaTdmOperator(BaseOperator):

    @apply_defaults
    def __init__(self, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler

    def execute(self, context):
        logger.info(f"airflow context: {context}")
        task_handler = utils.lazy_import(self.handler)
        return task_handler(**context)


class EmsaTdmPlugin(AirflowPlugin):
    name = "emsa_tdm_plugin"
    operators = [
        EmsaTdmOperator,
    ]


