"""
Glue PySpark ETL script to upload playlists table to the RDS.

Input paramaters:
--dataset               Dataset to use

Additional parameters:
--additional-python-modules=ssm-cache==2.10

Author: Heorhii Torianyk <deadstonepro@gmail.com>
Version: 0.0.4
"""

import sys
import logging

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
OUTPUT_RDS_TABLE_NAME = "playlists"


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


logger.debug("Input Catalog database: %s", CATALOG_DATABASE_SSM.value)
logger.debug("Input Catalog table: %s", CATALOG_TABLE)
logger.debug("Output Glue connection: %s", GLUE_CONNECTION_SSM.value)
logger.debug("Output RDS database name: %s", DATABASE_NAME_SSM.value)


class LoadArtistsETL:

    def __init__(self):
        params = ["dataset"]

        if "--JOB_NAME" in sys.argv:
            params.append("JOB_NAME")

        args = getResolvedOptions(sys.argv, params)

        self.dataset = args["dataset"]
        logger.debug("Input dataset: %s", self.dataset)

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
        Extracts distinct playlists from the given DynamicFrame.
        :param dyf: Input dynamic frame.
        :type dif: DynamicFrame
        :return: Relationalized and cleaned dynamic frame.
        :rtype: DynamicFrame
        """

        playlist_records = ApplyMapping.apply(dyf, [
            ("playlist_id", "number", "id", "string"),
            ("playlist_name", "string", "name", "string")
        ])

        playlists_df = playlist_records.toDF().drop_duplicates(["id"])

        return DynamicFrame.fromDF(playlists_df, self.glue_context, OUTPUT_RDS_TABLE_NAME)

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
