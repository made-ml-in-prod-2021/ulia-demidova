import os

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago

from .utils import default_args, VOLUME


with DAG(
    dag_id="03-predict",
    default_args=default_args,
    sheduler_interval="@daily",
    start_date=days_ago(1)
) as dag:
    data_sensor = FileSensor(
        task_id="wait_for_data",
        filepath=os.path.join("/data/raw/{{ ds }}", "data.csv"),
        timeout=6000,
        poke_interval=10,
        retries=100,
    )

    model_sensor = FileSensor(
        task_id="wait_for_model",
        filepath=os.path.join("{{ var.value.MODEL_DIR }}", "model.pkl"),
        timeout=6000,
        poke_interval=10,
        retries=100,
    )

    predict = DockerOperator(
        image="airflow-predict",
        command="--input-dir /data/raw/{{ ds }} --model-dir {{ var.value.MODEL_DIR }} "
                "--output-dir /data/predictions/{{ ds }}",
        network_mode="bridge",
        task_id="docker-airflow-predict",
        do_xcom_push=False,
        volumes=[VOLUME]
    )

    [data_sensor, model_sensor] >> predict
