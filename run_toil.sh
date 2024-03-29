#!/bin/bash
toil=$1
jobStore=$2
inputs=$3
out_dir=$4
log_file=$5

GUID=$6
API_KEY=$7

rootFolder=$8

python3 $toil $jobStore $inputs $out_dir --logFile $log_file
cwd=$(pwd)
cd ${rootFolder}
python3 $pythonScript $GUID $API_KEY $cwd