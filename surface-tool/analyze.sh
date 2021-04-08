#!/bin/sh
DATA_PATH="path/to/processed-surf-dataset"
METRIC="Undefined"

while getopts m:p:n:r: option
do
case "${option}"
in
m) METRIC=${OPTARG};;
p) PERIOD=${OPTARG};;
n) NODES=${OPTARG};;
r) RACKS=${OPTARG};;
esac
done

python3 ./surfsara-tool/main/main.py --path=$DATA_PATH --metric=$METRIC  --period=$PERIOD --nodes=$NODES --racks=$RACKS
