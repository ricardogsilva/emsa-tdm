"""Draft for production DAGs"""

import datetime as dt
import json
import pathlib
import sys

from airflow import configuration
from airflow import DAG
from airflow.operators import subdag_operator
from airflow.operators import EmsaTdmOperator
import shapely.wkt

sys.path.append(configuration.get("core", "airflow_home"))

from processing import tiles
from processing import utils



# TODO: use the same executor for subdags as the one in airflow.cfg

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": dt.datetime(2018, 11, 1),
    "email": [
        "ricardo.silva@geo-solutions.it"
    ],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": dt.timedelta(minutes=5),
}


def get_settings():
    home = configuration.get("core", "airflow_home")
    settings_path = pathlib.Path(home) / "tests/data/test-settings.json"
    with settings_path.open() as fh:
        return json.load(fh)


def generate_production_dag(settings):
    home = configuration.get("core", "airflow_home")
    dag = DAG(
        "production_draft",
        description="A draft DAG for using airflow inside docker",
        default_args=default_args,
        schedule_interval=dt.timedelta(days=1)
    )
    dag.doc_md = """# This is some documentation for the DAG"""
    with dag:
        all_vessels_tdm_task = EmsaTdmOperator(
            task_id="all_vessels_tdm",
            handler=f"{home}/processing/tasks.py:generate_all_vessels_tdm",
        )
        for vessel_config in settings["vessels"]:
            vessel_subdag_id = f"{vessel_config['name']}_tdm"
            vessel_subdag = subdag_operator.SubDagOperator(
                task_id=vessel_subdag_id,
                subdag=generate_vessel_dag(
                    vessel_config["name"],
                    f"{dag.dag_id}.{vessel_subdag_id}",
                    settings
                ),
            )
            vessel_subdag >> all_vessels_tdm_task

    return dag


def generate_vessel_dag(vessel, dag_id, settings):
    home = configuration.get("core", "airflow_home")
    dag = DAG(
        dag_id=dag_id,
        description="",
        default_args=default_args,
    )
    with dag:
        tile_aggregator_task = EmsaTdmOperator(
            task_id=f"{vessel}_tile_aggregator",
            handler=f"{home}/processing/tasks.py:aggregate_tiles",
        )
        num_tiles = tiles.adjust_num_tiles(settings["processing_tiles"])
        for tile in range(num_tiles):
            tile_subdag_id = f"tile_{tile:03d}"
            tile_subdag = subdag_operator.SubDagOperator(
                task_id=tile_subdag_id,
                subdag=generate_tile_dag(
                    tile,
                    vessel,
                    f"{dag.dag_id}.{tile_subdag_id}",
                    settings,
                )
            )
            tile_subdag >> tile_aggregator_task
    return dag


def generate_tile_dag(tile, vessel, dag_id, settings, dag_params=None):
    home = configuration.get("core", "airflow_home")
    dag = DAG(
        dag_id,
        description="",
        default_args=default_args,
        params=dag_params
    )
    grid = tiles.build_grid(
        shapely.wkt.loads(settings["region_of_interest"]),
        settings["processing_tiles"]
    )
    tile_polygon, grid_coordinates = grid[tile]
    dag.doc_md = f"tile {tile} wkt: {tile_polygon.wkt}"
    with dag:
        vessel_config = utils.get_vessel_settings(settings, vessel)
        # vessel_config = [
        #     item for item in settings["vessels"] if item["name"] == vessel][0]
        merge_sensor_data_task = EmsaTdmOperator(
            task_id="merge_sensor_data",
            handler=f"{home}/processing/tasks.py:merge_data",
        )
        filter_invalid_positions_task = EmsaTdmOperator(
            task_id="filter_invalid_positions",
            handler=f"{home}/processing/tasks.py:filter_invalid_positions",
        )
        build_routes_task = EmsaTdmOperator(
            task_id="build_routes",
            handler=f"{home}/processing/tasks.py:build_routes",
        )
        filter_invalid_routes_task = EmsaTdmOperator(
            task_id="filter_invalid_routes",
            handler=f"{home}/processing/tasks.py:filter_invalid_routes",
        )
        build_tdm_task = EmsaTdmOperator(
            task_id="build_tdm",
            handler=f"{home}/processing/tasks.py:build_tdm",
        )
        for sensor_config in settings["sensor_types"]:
            sensor = sensor_config["name"]
            retrieve_data_task = EmsaTdmOperator(
                task_id=f"{sensor}_retrieve_data",
                handler=f"{home}/processing/tasks.py:retrieve_data",
                params={
                    "sensor": sensor,
                    "tile": tile,
                    "vessel": vessel,
                }
            )
            pre_process_sensor_data_task = EmsaTdmOperator(
                task_id=f"{sensor}_preprocess_data",
                handler=f"{home}/processing/tasks.py:pre_process_data",
            )
            retrieve_data_task >> pre_process_sensor_data_task
            pre_process_sensor_data_task >> merge_sensor_data_task
        merge_sensor_data_task >> filter_invalid_positions_task
        filter_invalid_positions_task >> build_routes_task
        build_routes_task >> filter_invalid_routes_task
        filter_invalid_routes_task >> build_tdm_task

    return dag


prod_dag = generate_production_dag(get_settings())
