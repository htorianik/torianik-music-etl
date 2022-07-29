#!/bin/bash

SCRIPT_FILE_NAME=$1
ARGS=${@:2}


WORKSPACE_LOCATION=/home/htorianik/personal/torianik-music-etl/resources
PROFILE_NAME=personal

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
