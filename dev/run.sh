#!/bin/bash


IMAGE_NAME=htorianik-music-glue-env
WORKSPACE_LOCATION=/home/htorianik/personal/torianik-music-etl/resources
PROFILE_NAME=personal
SCRIPT_FILE_NAME=$1
ARGS=${@:2}

if [ -n "$(docker images -q ${IMAGE_NAME})" ]; then
    docker build -t $IMAGE_NAME
fi

docker run -it \
    -v ~/.aws:/home/glue_user/.aws \
    -v $WORKSPACE_LOCATION:/home/glue_user/workspace/ \
    -e AWS_PROFILE=$PROFILE_NAME \
    -e AWS_REGION=us-east-1 \
    -e DISABLE_SSL=true \
    --rm \
    --network host \
    --name glue_spark_submit \
    $IMAGE_NAME spark-submit /home/glue_user/workspace/$SCRIPT_FILE_NAME $ARGS
