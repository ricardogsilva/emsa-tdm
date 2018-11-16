"""Docker entrypoint script 

This script has been adapted from the puckel/docker-airflow docker repository.

This script is used to make sure the various services start up when their
dependencies are available.

Airflow roles ``webserver``, ``scheduler`` and ``worker`` must only start
once the ``postgres`` and ``redis`` servers are ready to accept requests.

Additionally, in order for any of the previously mentioned airflow roles to
work, the airflow database must have been initialized.

We use the ``webserver`` role to also initialize the database before
launching. Meanwhile the other roles are sleeping.

"""

import argparse
import logging
import os
import pathlib
from subprocess import call, PIPE
from time import sleep

from airflow import configuration
from airflow.bin.cli import CLIFactory
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)
DB_INIT_WAITING_SECONDS = 10


def create_environment():
    """Put docker secrets in the environment"""

    for item in pathlib.Path("/run/secrets").iterdir():
        if item.is_file():
            contents = item.read_text()
            os.putenv(item.name, contents)
            os.environ[item.name] = contents


def run_flower(args, remaining_args):
    _launch_airflow(["flower"] + remaining_args)


def run_scheduler(args, remaining_args):
    _handle_database_setup()
    _handle_executor_setup()
    _launch_airflow(["scheduler"] + remaining_args)


def run_webserver(args, remaining_args):
    _handle_database_setup(initdb=True)
    _handle_executor_setup()
    _launch_airflow(["webserver"] + remaining_args)


def run_worker(args, remaining_args):
    _handle_database_setup()
    _handle_executor_setup()
    _launch_airflow(["worker"] + remaining_args)


def _handle_database_setup(initdb=False):
    db_config_value = _get_db_url()
    if "postgres" in db_config_value:
        _wait_for_postgres()
    if initdb:
        _launch_airflow(["initdb"])
    else:
        sleep(DB_INIT_WAITING_SECONDS)  # await db init by ``web`` container


def _handle_executor_setup():
    if "celery" in configuration.get("core", "executor").lower():
        _wait_for_redis()


def _launch_airflow(args):
    # os.execlp("airflow", *args)
    airflow_parser = CLIFactory.get_parser()
    airflow_args = airflow_parser.parse_args(args)
    airflow_args.func(airflow_args)


def _get_db_url():
    config_section = configuration.getsection("core")
    connection_config_command = config_section.get("sql_alchemy_conn_cmd")
    if connection_config_command is not None:
        result = configuration.run_command(connection_config_command)
    else:
        result = configuration.get("sql_alchemy_conn")
    return result


def _wait_for_postgres(max_tries=10, wait_seconds=3):
    database_url = _get_db_url()
    engine = create_engine(database_url)
    current_try = 0
    while current_try < max_tries:
        try:
            engine.execute("SELECT version();")
            logger.debug("Database is already up!")
            break
        except OperationalError:
            logger.debug("Database not responding yet ...")
            current_try += 1
            sleep(wait_seconds)
    else:
        raise RuntimeError(
            "Database not responding at {} after {} tries. "
            "Giving up".format(database_url, max_tries)
        )


def _wait_for_redis():
    return _wait_for_network_service("redis", "6379")


def _wait_for_network_service(host, port, max_tries=10, wait_seconds=3):
    print("Waiting for {!r}:{!r}...".format(host, port))
    current_try = 0
    while current_try < max_tries:
        return_code = call(
            ["netcat", "-z", str(host), str(port)], stdout=PIPE, stderr=PIPE)
        if int(return_code) == 0:
            print("{!r}:{!r} is already up!".format(host, port))
            break
        else:
            current_try += 1
            sleep(wait_seconds)
    else:
        raise RuntimeError("Could not find {}:{} after {} tries. "
                           "Giving up".format(host, port, max_tries))


def _get_parser():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    for sub_command in ["webserver", "worker", "scheduler", "flower"]:
        sub_parser = sub_parsers.add_parser(sub_command)
        func = globals()["run_{}".format(sub_command)]
        sub_parser.set_defaults(func=func)
    return parser


if __name__ == "__main__":
    parser = _get_parser()
    args, remaining_args = parser.parse_known_args()
    create_environment()
    args.func(args, remaining_args)
