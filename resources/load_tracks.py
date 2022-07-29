"""
Glue PySpark ETL script to upload tracks table to the RDS.

Input paramaters:
--dataset               Dataset to use

Additional parameters:
--additional-python-modules=ssm-cache==2.10

Author: Heorhii Torianyk <deadstonepro@gmail.com>
"""

import sys

from ssm_cache import SSMParameter

from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import ApplyMapping
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


SSM_PREFIX = "/torianik-music/dev/"
DATABASE_NAME_SSM = SSMParameter(f"{SSM_PREFIX}database_name")
GLUE_CONNECTION_SSM = SSMParameter(f"{SSM_PREFIX}glue_connection")
CATALOG_DATABASE_SSM = SSMParameter(f"{SSM_PREFIX}catalog_database")

CATALOG_TABLE = "clean"
OUTPUT_RDS_TABLE_NAME = "tracks"


class LoadArtistsETL:

    def __init__(self):
        params = ["dataset"]

        if "--JOB_NAME" in sys.argv:
            params.append("JOB_NAME")

        args = getResolvedOptions(sys.argv, params)

        self.dataset = args["dataset"]

        self.spark_context = SparkContext.getOrCreate()
        self.spark_context.setLogLevel("ERROR")
        self.glue_context = GlueContext(self.spark_context)
        self.job = Job(self.glue_context)

        if "JOB_NAME" in args:
            jobname = args["JOB_NAME"]
        else:
            jobname = "torianik-music-etl-job-run"
        self.job.init(jobname, args)

    def extract(self):
        """
        Extract data from Glue Catalog.
        :return: Retrieved DynamicFrame
        :rtype: DynamicFrame
        """
        return self.glue_context.create_dynamic_frame.from_catalog(
            database=CATALOG_DATABASE_SSM.value,
            table_name=CATALOG_TABLE,
            push_down_predicate=f"(dataset = '{self.dataset}')",
        )

    def transform(self, dyf):
        """
        Extracts distinct tracks from the given DynamicFrame.
        :param dyf: Input dynamic frame.
        :type dif: DynamicFrame
        :return: Relationalized and cleaned dynamic frame.
        :rtype: DynamicFrame
        """

        track_records = ApplyMapping.apply(dyf, [
            ("track_id", "string", "id", "string"),
            ("track_name", "string", "name", "string"),
            ("artist_id", "string", "artist_id", "string"),
        ])

        tracks_df = track_records.toDF().drop_duplicates(["id"])

        return DynamicFrame.fromDF(tracks_df, self.glue_context, OUTPUT_RDS_TABLE_NAME)

    def load(self, dyf):
        """
        Uploads DataFrame to RDS table using Glue JDBC Connection.
        :param dyf: DynamicFrame to write.
        :type dyf: DynamicFrame
        """
        self.glue_context.write_dynamic_frame_from_jdbc_conf(
            frame=dyf,
            catalog_connection=GLUE_CONNECTION_SSM.value,
            connection_options={
                "database": DATABASE_NAME_SSM.value,
                "dbtable": OUTPUT_RDS_TABLE_NAME,
            }
        )

    def run(self):
        """
        Entry point to the ETL script.
        """
        input_df = self.extract()
        output_df = self.transform(input_df)
        self.load(output_df)


if __name__ == "__main__":
    LoadArtistsETL().run()
