#!/bin/bash

WORKSPACE_LOCATION=/home/htorianik/personal/torianik-music-etl/resources   # Enter folder with a script
SCRIPT_FILE_NAME=etl_job.py                                                # Enter name of a script
PROFILE_NAME=personal                                                      # Enter local AWS profile that grants sufficient permissions

docker run -it \
    -v ~/.aws:/home/glue_user/.aws \
    -v $WORKSPACE_LOCATION:/home/glue_user/workspace/ \
    -e AWS_PROFILE=$PROFILE_NAME \
    -e AWS_REGION=us-east-1 \
    -e DISABLE_SSL=true \
    --rm \
    --network host \
    --name glue_spark_submit \
    htorianik-music-glue-env spark-submit /home/glue_user/workspace/$SCRIPT_FILE_NAME --catalog_table=759551559257_torianik_music_dev_data_lake
