import sys

from pyspark.sql import DataFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import explode
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


def get_ssm_value(ssm_client, name: str) -> str:
    pass


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

    def _show_df(self, name: str, df):
        print("Dataset", name)
        df.printSchema()
        df.show(3)


    def extract(self):
        return self.context.create_dynamic_frame.from_catalog(
            database="spotify_playlists",
            table_name="mini_mini",
        )

    def load(self, table_name: str, df):
        dyf = DynamicFrame.fromDF(df, self.context, table_name)

        connection_postgres_options = {
            "database": "postgres",
            "dbtable": table_name,
        }

        self.context.write_dynamic_frame_from_jdbc_conf(
            frame=dyf,
            catalog_connection="rds-test-postgresql",
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