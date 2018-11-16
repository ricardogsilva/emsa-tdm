FROM ubuntu:18.04

RUN adduser --uid 1000 --gecos '' --disabled-password airflow

RUN apt update \
  && apt install --yes \
    git \
    libgdal-dev \
    libssl-dev \
    netcat \
    python3-pip \
  && python3 -m pip install --upgrade pip \
  && mkdir -p /var/log/airflow \
  && chown airflow:airflow /var/log/airflow

WORKDIR /home/airflow

COPY requirements.txt requirements.txt

ENV AIRFLOW_GPL_UNIDECODE=yes \
  AIRFLOW_HOME=/home/airflow

RUN chown 1000:1000 requirements.txt \
  && python3 -m pip install --requirement requirements.txt

COPY . .

RUN chown --recursive 1000:1000 *

USER airflow

EXPOSE 8080 5555 8793

ENTRYPOINT ["python3", "/home/airflow/docker/docker-entrypoint.py"]

CMD ["webserver"]
