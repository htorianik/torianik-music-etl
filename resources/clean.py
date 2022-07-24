"""
Glue PySpark ETL script to relationalize and clean the data.

Input paramaters:
--dataset               Dataset to use

Additional parameters:
--additional-python-modules=ssm-cache==2.10

Author: Heorhii Torianyk <deadstonepro@gmail.com>
Version: 0.1.0
"""

import sys
import logging

from ssm_cache import SSMParameter

from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.transforms import ApplyMapping, Join
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


SSM_PREFIX = "/torianik-music/dev/"
DATA_LAKE_BUCKET_SSM = SSMParameter(f"{SSM_PREFIX}data_lake_bucket")
CATALOG_DATABASE_SSM = SSMParameter(f"{SSM_PREFIX}catalog_database")

CATALOG_TABLE = "raw"
TEMP_PATH = f"s3://{DATA_LAKE_BUCKET_SSM.value}/temp"
OUTPUT_PATH = f"s3://{DATA_LAKE_BUCKET_SSM.value}/clean"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("Input Catalog database: %s", CATALOG_DATABASE_SSM.value)
logger.info("Input Catalog table: %s", CATALOG_TABLE)
logger.info("Temp S3 path: %s", TEMP_PATH)
logger.info("Output s3 path: %s", OUTPUT_PATH)


class CleanETL:

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
        Relationalize and clean the dynamic frame.
        :param dyf: Input dynamic frame.
        :type dif: DynamicFrame
        :return: Relationalized and cleaned dynamic frame.
        :rtype: DynamicFrame
        """
        dfc = dyf.relationalize("root", TEMP_PATH)

        tracks_dirty = Join.apply(dfc.select("root"), dfc.select("root_tracks"), "tracks", "id")

        tracks = ApplyMapping.apply(tracks_dirty, [
            ("pid", "int", "playlist_id", "int"),
            ("name", "string", "playlist_name", "string"),
            ("track_uri", "string", "track_id", "string"),
            ("track_name", "string", "track_name", "string"),
            ("artist_uri", "string", "artist_id", "string"),
            ("artist_name", "string", "artist_name", "string"),
            ("dataset", "string", "dataset", "string"),
        ])

        return tracks

    def load(self, dyf):
        """
        Uploads DataFrame to S3 Bucket as few Apache parquet files.
        :param dyf: DynamicFrame to write.
        :type dyf: DynamicFrame
        """
        self.glue_context.write_dynamic_frame.from_options(
            frame=dyf, 
            connection_type="s3",
            connection_options={
                "path": OUTPUT_PATH,
                "partitionKeys": ["dataset"],
            },
            format="parquet"
        )

    def run(self):
        """
        Entry point to the ETL script.
        """
        input_df = self.extract()
        output_df = self.transform(input_df)
        self.load(output_df)


if __name__ == "__main__":
    CleanETL().run()
