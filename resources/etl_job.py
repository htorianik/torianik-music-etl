"""
Glue PySpark script for ETL-job to load 
1m spotify playlists from Glue Catalog to RDS.

:author: Heorhii Torianyk <deadstonepro@gmail.com>

Script version: 0.1.1
"""

import io
import sys
import logging
from contextlib import contextmanager

import boto3
import psycopg2
from ssm_cache import SSMParameter
from pyspark.context import SparkContext
from pyspark.sql.functions import explode
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SSM_PREFIX = "/torianik-music/dev/"
DATABASE_HOST_SSM = SSMParameter(f"{SSM_PREFIX}database_host")
DATABASE_NAME_SSM = SSMParameter(f"{SSM_PREFIX}database_name")
DATABASE_USER_SSM = SSMParameter(f"{SSM_PREFIX}database_user")
DATABASE_PASSWORD_SSM = SSMParameter(f"{SSM_PREFIX}database_password")
CATALOG_DATABASE_SSM = SSMParameter(f"{SSM_PREFIX}catalog_database")
SOURCES_BUCKET_SSM = SSMParameter(f"{SSM_PREFIX}sources_bucket")

DATABASE_PORT = 5432
CREATE_TABLES_SQL_KEY = "create_tables.sql"


logger.info("Sources bucket: %s", SOURCES_BUCKET_SSM.value)


class TorianikMusicETL:
    """
    Class to manage the ETL job execution.
    Entry point is TorianikMusicETL.run().
    """

    def __init__(self):
        params = ["catalogTable"]
        if "--JOB_NAME" in sys.argv:
            params.append("JOB_NAME")

        args = getResolvedOptions(sys.argv, params)

        self.catalog_table = args["catalogTable"]
        self.spark_context = SparkContext.getOrCreate()
        self.spark_context.setLogLevel("ERROR")
        self.glue_context = GlueContext(self.spark_context)
        self.job = Job(self.glue_context)

        if "JOB_NAME" in args:
            jobname = args["JOB_NAME"]
        else:
            jobname = "torianik-music-etl-job-run"
        self.job.init(jobname, args)

    def load_source_from_s3(self, path):
        """
        Retrieve a file from s3 bucket of sources.
        :param path: Key of the s3 object.
        :type path: str
        :return: String with content of a file.
        :rtype: str
        """
        s3 = boto3.client("s3")
        fileobj = io.BytesIO()
        s3.download_fileobj(
            SOURCES_BUCKET_SSM.value,
            path,
            fileobj,
        )
        fileobj.flush()
        fileobj.seek(0)
        return fileobj.read().decode("utf-8")

    @contextmanager
    def postgresql_cursor(self):
        """
        Context manager to create and ensure the closure
        of the postgresql connection to a target database.
        Yield the cursor.
        """
        params = {
            "dbname": DATABASE_NAME_SSM.value,
            "user": DATABASE_USER_SSM.value,
            "password": DATABASE_PASSWORD_SSM.value,
            "host": DATABASE_HOST_SSM.value,
            "port": DATABASE_PORT,
        }
        conn = psycopg2.connect(**params)
        try:
            with conn:
                with conn.cursor() as curs:
                    yield curs
        except:
            conn.close()
            raise

    def pre_load(self):
        """
        Actions to perform the before data loading.
        """
        query = self.load_source_from_s3(CREATE_TABLES_SQL_KEY)
        with self.postgresql_cursor() as cursor:
            cursor.execute(query)

    def extract(self):
        """
        Loads dynamic frame from Catalog, converts it to a data frame.
        :return: DataFrame created from Glue Catalog table.
        :rtype: pyspark.datagrame.DataFrame
        """
        return self.glue_context.create_dynamic_frame.from_catalog(
            database=CATALOG_DATABASE_SSM.value,
            table_name=self.catalog_table,
        ).toDF()

    def load(self, dfs):
        """
        Loads data frames into RDS database.
        :param dfs: Tuple of data frames that represents artists, tracks, playlists, edges
        :type dfs: (pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame)
        """
        (artists_df, tracks_df, plyalists_df, edges_df) = dfs
        self.load_df_as_table("artists", artists_df)
        self.load_df_as_table("tracks", tracks_df)
        self.load_df_as_table("playlists", plyalists_df)
        self.load_df_as_table("edges", edges_df)

    def load_df_as_table(self, table_name, df):
        """
        Loads data frame into RDS database's table.
        :param table_name: Name of table to load data into.
        :type table_name: str
        :param df: Data frame to upload.
        :type df: pyspark.dataframe.DataFrame
        """
        dyf = DynamicFrame.fromDF(df, self.glue_context, table_name)
        jdbc_url = f"jdbc:postgresql://{DATABASE_HOST_SSM.value}:5432/{DATABASE_NAME_SSM.value}"
        connection_postgres_options = {
            "url": jdbc_url,
            "user": "postgres",
            "password": DATABASE_PASSWORD_SSM.value,
            "dbtable": table_name,
        }
        self.glue_context.write_from_options(
            dyf,
            connection_type="postgresql",
            connection_options=connection_postgres_options,
        )
        logger.info("DataFrame is loaded as %s.%s", DATABASE_NAME_SSM.value, table_name)

    def transform(self, df):
        """
        Transforms the input df into 4 df: artists, tracks, playlists, edges.
        :param df: Input dataframe with schema of the source datacet (See README).
        :type df: class: pyspark.dataframe.DataFrame
        :return: Tuple of 4 dataframes (artists, tracks, playlists, edges).
        :rtype: (pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame, pyspark.dataframe.DataFrame)
        """
        df1 = df.select(df["pid"], df["name"], explode(df["tracks"]).alias("track"))

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

        return artists, tracks, playlists, edges

    def run(self):
        input_df = self.extract()
        output_dfs = self.transform(input_df)
        self.pre_load()
        self.load(output_dfs)
        self.job.commit()


if __name__ == "__main__":
    TorianikMusicETL().run()
