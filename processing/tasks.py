"""airflow tasks"""

import logging

logger = logging.getLogger(__name__)


def retrieve_data(yesterday_ds, params, **context):
    logger.info(f"context: {context}")
    logger.info(f"yesterday_ds: {yesterday_ds}")
    sensor = params.get("sensor")
    tile = params.get("tile")
    logger.info(f"sensor: {sensor}")
    logger.info(f"tile: {tile}")


def pre_process_data(**context):
    logger.info("hi, this is the pre_process_data task")


def aggregator(**context):
    logger.info("hi, this is the aggregator task")
