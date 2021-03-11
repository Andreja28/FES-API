workflow=$2
inputs=$3
GUID=$4
API_KEY=$5

rootFolder=$6

if [ $1 == "y" ]
then
    readOnly="--no-read-only --no-match-user"
else
    readOnly=""
fi


cwltool $readOnly $workflow $inputs
cwd=$(pwd)
cd ${rootFolder}
python3 girder-upload.py $GUID $API_KEY $cwd