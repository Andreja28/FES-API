jobStore=$2
logFile=$3
workflow=$4
inputs=$5

GUID=$6
API_KEY=$7

pythonScript=$8

if [ $1 == "y" ]
then
    readOnly="--no-read-only --no-match-user"
else
    readOnly=""
fi


`toil-cwl-runner $readOnly --jobStore $jobStore --logFile $logFile $workflow $inputs`
cwd=`pwd`
python3 $pythonScript $GUID $API_KEY 