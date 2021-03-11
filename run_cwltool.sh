workflow=$2
inputs=$3

GUID=$4
API_KEY=$5

pythonScript=$6

if [ $1 == "y" ]
then
    readOnly="--no-read-only --no-match-user"
else
    readOnly=""
fi


`cwltool $readOnly $workflow $inputs`
cwd=`pwd`
python3 $pythonScript $GUID $API_KEY 