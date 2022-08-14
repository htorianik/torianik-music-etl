"""
Apache Ariflow DAG that manages Crawlers, DB, ETL Jobs of torianik-music-etl.

Trigger DAG w/ config:
```json
{
    "dataset": "dataset you want to process"
}
```

Author: Heorhii Torianyk <deadstonepro@gmail.com>
"""

import datetime
from typing import Dict, Sequence

from ssm_cache import SSMParameter
from airflow import models
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.glue import GlueJobHook
from airflow.providers.amazon.aws.hooks.glue_crawler import GlueCrawlerHook
from airflow.providers.postgres.operators.postgres import PostgresOperator


SOURCES_BUCKET_SSM = SSMParameter(f"/torianik-music/dev/sources_bucket")
INIT_DB_SQL_KEY = "create_tables.sql"


yesterday = datetime.datetime.combine(
    datetime.datetime.today() - datetime.timedelta(1), datetime.datetime.min.time()
)


class CrawlerOperator(models.BaseOperator):
    def __init__(self, crawler_name: str, **kwargs):
        super().__init__(**kwargs)
        self.hook = GlueCrawlerHook()
        self.crawler_name = crawler_name

    def execute(self, context):
        self.hook.start_crawler(self.crawler_name)
        self.hook.wait_for_crawler_completion(self.crawler_name)
        return "OK"


class EtlJobOperator(models.BaseOperator):

    job_name: str
    script_args: Dict[str, str]

    template_fields: Sequence[str] = ("job_name", "script_args")

    def __init__(self, job_name: str, script_args: Dict[str, str] = {}, **kwargs):
        super().__init__(**kwargs)
        self.hook = GlueCrawlerHook()
        self.job_name = job_name
        self.script_args = {
            "--additional-python-modules": "ssm-cache==2.10",
            **script_args,
        }

    def execute(self, context):
        glue_hook = GlueJobHook(job_name=self.job_name)

        run_id = glue_hook.initialize_job(script_arguments=self.script_args)["JobRunId"]

        glue_hook.job_completion(
            job_name=self.job_name,
            run_id=run_id,
        )

        return "OK"


def get_init_db_sql():
    s3_hook = S3Hook()
    s3_client = s3_hook.get_conn()
    file_obj = s3_client.get_object(
        Bucket=SOURCES_BUCKET_SSM.value, Key=INIT_DB_SQL_KEY
    )
    file_content = file_obj["Body"].read().decode("utf-8")
    return file_content


with models.DAG(
    "torianik-music-etl-dag",
    default_args={
        "start_date": yesterday,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
        "retry_delay": datetime.timedelta(minutes=5),
        "concurrency": 2,
    },
    params={"dataset": models.Param(default="first-10")},
) as dag:

    crawl_raw = CrawlerOperator(
        task_id="crawl_raw",
        crawler_name="torianik-music-dev-crawler-raw",
        dag=dag,
    )

    crawl_clean = CrawlerOperator(
        task_id="crawl_clean",
        crawler_name="torianik-music-dev-crawler-clean",
        dag=dag,
    )

    clean_etl = EtlJobOperator(
        task_id="clean_etl",
        job_name="torianik-music-dev-clean",
        script_args={"--dataset": "{{ params.dataset }}"},
        dag=dag,
    )

    init_db = PostgresOperator(
        task_id="init_db",
        sql=get_init_db_sql(),
        dag=dag,
    )

    load_artists_etl = EtlJobOperator(
        task_id="load_artists_etl",
        job_name="torianik-music-dev-load_artists",
        script_args={"--dataset": "{{ params.dataset }}"},
        dag=dag,
    )

    load_edges_etl = EtlJobOperator(
        task_id="load_edges_etl",
        job_name="torianik-music-dev-load_edges",
        script_args={"--dataset": "{{ params.dataset }}"},
        dag=dag,
    )

    load_playlists_etl = EtlJobOperator(
        task_id="load_playlists_etl",
        job_name="torianik-music-dev-load_playlists",
        script_args={"--dataset": "{{ params.dataset }}"},
        dag=dag,
    )

    load_tracks_etl = EtlJobOperator(
        task_id="load_tracks_etl",
        job_name="torianik-music-dev-load_tracks",
        script_args={"--dataset": "{{ params.dataset }}"},
        dag=dag,
    )

    (
        crawl_raw
        >> clean_etl
        >> crawl_clean
        >> init_db
        >> [load_artists_etl, load_playlists_etl]
    )

    load_tracks_etl << load_artists_etl

    load_edges_etl << [load_tracks_etl, load_playlists_etl]
