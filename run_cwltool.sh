workflow=$2
inputs=$3

GUID=$4
API_KEY=$5

if [ $1 == "y" ]
then
    readOnly="--no-read-only --no-match-user"
else
    readOnly=""
fi


`cwltool $readOnly $workflow $inputs`
cwd=`pwd`
python3 girder-upload.py $cwd $GUID $API_KEY 