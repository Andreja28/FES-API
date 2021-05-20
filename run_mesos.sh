#!/bin/bash
jobStore=$2
logFile=$3
workflow=$4
inputs=$5

GUID=$6
API_KEY=$7

nodeType=$8
rootFolder=$9

if [ $1 == "y" ]
then
    readOnly="--no-read-only --no-match-user"
else
    readOnly=""
fi


toil-cwl-runner $readOnly --jobStore aws:us-west-2:$jobStore --provisioner aws --batchSystem mesos --nodeType $nodeType --realTimeLogging --logInfo --disableCaching False --logFile $logFile $workflow $inputs
cwd=$(pwd)
cd ${rootFolder}
python3 $pythonScript $GUID $API_KEY $cwd