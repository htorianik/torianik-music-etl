#!/usr/bin/python3

"""
Util to extract and upload slices of 1 million spotify playlists
dataset into s3 bucket.

USAGE:
    ./utils/unpack.py --help

:author: Heorhii Torianyk <deadstonepro@gmail.com>
"""

import zipfile
import argparse
import logging
from typing import List
from datetime import datetime
from concurrent import futures

import boto3  # type: ignore
import botocore  # type: ignore


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def _inflate_to_s3(
    s3_client,
    zip_ref: zipfile.ZipFile,
    zip_path: str,
    target_bucket: str,
    key_prefix: str,
):
    fileobj = zip_ref.open(zip_path)
    key = f"{key_prefix}/{zip_path}"
    s3_client.upload_fileobj(fileobj, target_bucket, key)
    logger.info("%s was unarchived and uploaded as %s", zip_path, key)


def inflate_to_s3_multiple(
    zip_ref: zipfile.ZipFile,
    zip_files: List[str],
    target_bucket: str,
    key_prefix: str,
):
    s3_client = boto3.client(
        "s3",
        config=botocore.config.Config(
            max_pool_connections=100,
        ),
    )

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        fs = (
            executor.submit(
                _inflate_to_s3,
                s3_client,
                zip_ref,
                zip_path,
                target_bucket,
                key_prefix,
            )
            for zip_path in zip_files
        )
        list(futures.as_completed(fs))


def unpack_to_s3(
    input_path: str,
    target_bucket: str,
    prefix: str = "",
    nslices: int = -1,
):
    key_prefix = f"{prefix}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

    with zipfile.ZipFile(input_path, "r") as zip_ref:
        data_files = [file for file in zip_ref.namelist() if file.startswith("data/")]

        if nslices != -1:
            data_files = data_files[:nslices]

        inflate_to_s3_multiple(
            zip_ref,
            data_files,
            target_bucket,
            key_prefix,
        )


parser = argparse.ArgumentParser(
    description="Inflates the archive and uploads it to S3"
)
parser.add_argument("--bucket", type=str, help="Bucket to upload into.")
parser.add_argument("--input", type=str, help="Path to the input archive.")
parser.add_argument(
    "--prefix", type=str, default="raw", help="Prefix for a output s3 objects."
)
parser.add_argument(
    "--nslices",
    type=int,
    default=-1,
    help="Number of slices to extract. -1 for unpacking all files (default: -1).",
)


if __name__ == "__main__":
    args = parser.parse_args()
    unpack_to_s3(
        args.input,
        args.bucket,
        args.prefix,
        args.nslices,
    )
