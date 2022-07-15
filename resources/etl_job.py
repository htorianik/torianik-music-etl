import sys
import logging
from typing import Union, List

import boto3
from pyspark.sql import DataFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import explode
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GLUE_CONNECTION_NAME_SSM = "/torianik-music/dev/glue_connection_name"
CATALOG_DATABASE_NAME_SSM = "/torianik-music/dev/catalog_database_name"
DATABASE_NAME_SSM = "/torianik-music/dev/database_name"
CATALOG_TABLE_NAME = "set-up-me"


def get_ssm_value(ssm_client, name: str) -> Union[str, List[str]]:
    resp = ssm_client.get_parameter(Name=name)
    param = resp["Parameter"]
    if not param["Type"] in ["String", "StringList"]:
        raise NotImplementedError("Only String and StringList param types are supported.")
    
    return param["Value"]


class GluePythonSampleTest:
    def __init__(self):
        params = []
        if '--JOB_NAME' in sys.argv:
            params.append('JOB_NAME')
        args = getResolvedOptions(sys.argv, params)

        self.spark_context = SparkContext.getOrCreate()
        self.spark_context.setLogLevel("ERROR")
        self.context = GlueContext(self.spark_context)
        self.job = Job(self.context)

        if 'JOB_NAME' in args:
            jobname = args['JOB_NAME']
        else:
            jobname = "test"
        self.job.init(jobname, args)

        ssm_client = boto3.client("ssm")

        self.catalog_database_name = get_ssm_value(
            ssm_client,
            CATALOG_DATABASE_NAME_SSM, 
        )

        self.glue_connection_name = get_ssm_value(
            ssm_client,
            GLUE_CONNECTION_NAME_SSM,
        )

        self.database_name = get_ssm_value(
            ssm_client,
            DATABASE_NAME_SSM,
        )

        self.catalog_table_name = CATALOG_TABLE_NAME

        logger.info("Catalog Database: %s", self.catalog_database_name)
        logger.info("Catalog Table: %s", self.catalog_table_name)
        logger.info("Glue Connection: %s", self.glue_connection_name)
        logger.info("Dedicated Databse: %s", self.database_name)

    def extract(self):
        return self.context.create_dynamic_frame.from_catalog(
            database=self.catalog_database_name,
            table_name=self.catalog_table_name,
        )

    def load(self, table_name: str, df: DataFrame):
        dyf = DynamicFrame.fromDF(df, self.context, table_name)

        connection_postgres_options = {
            "database": self.database_name,
            "dbtable": table_name,
        }

        self.context.write_dynamic_frame_from_jdbc_conf(
            frame=dyf,
            catalog_connection=self.glue_connection_name,
            connection_options=connection_postgres_options,
        )

    def run(self):
        dyf = self.extract()
        dyf.printSchema()

        df = dyf.toDF()
        df1 = df.select(
            df["pid"],
            df["name"],
            explode(df["tracks"]).alias("track")
        )

        tracks = df1.select(
            df1["track"]["track_uri"].alias("id"),
            df1["track"]["track_name"].alias("name"),
            df1["track"]["artist_uri"].alias("artist_id"),
        ).drop_duplicates(["id"])

        artists = df1.select(
            df1["track"]["artist_uri"].alias("id"),
            df1["track"]["artist_name"].alias("name"),
        ).drop_duplicates(["id"])

        playlists = df1.select(
            df1["pid"].alias("id"),
            df1["name"].alias("name"),
        ).drop_duplicates(["id"])

        edges = df1.select(
            df1["pid"].alias("playlist_id"),
            df1["track"]["track_uri"].alias("track_id"),
        ).distinct()

        self.load("artists", artists)
        self.load("tracks", tracks)
        self.load("playlists", playlists)
        self.load("edges", edges)

        self.job.commit()


if __name__ == '__main__':
    GluePythonSampleTest().run()