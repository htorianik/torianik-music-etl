#!/bin/bash

WORKSPACE_LOCATION=/home/htorianik/personal/torianik-music-etl/resources
SCRIPT_FILE_NAME=clean.py
PROFILE_NAME=personal
ARGS="--catalogTable=first_1"

docker run -it \
    -v ~/.aws:/home/glue_user/.aws \
    -v $WORKSPACE_LOCATION:/home/glue_user/workspace/ \
    -e AWS_PROFILE=$PROFILE_NAME \
    -e AWS_REGION=us-east-1 \
    -e DISABLE_SSL=true \
    --rm \
    --network host \
    --name glue_spark_submit \
    htorianik-music-glue-env spark-submit /home/glue_user/workspace/$SCRIPT_FILE_NAME $ARGS
