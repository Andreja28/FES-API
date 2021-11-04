# FES-API

## Installation

```bash
sudo pip3 install virtualenv
cd FES-API
virtualenv  venv
. venv/bin/activate
pip3 install flask
pip3 install girder-client
pip3 install toil[all]
export FLASK_APP=hello.py
flask run
```

The file `config.py` contains variables `CWL` (path to folder containing CWL workflows), `TOIL` (path to folder containing Toil workflows), `RESULTS` (path to folder where the workflow results will be stored) and `RUNNING_WORKFLOWS` (path to folder where the temoporary workflow job stores will be located).



## Examples



### List of all workflow templates

```bash
curl -H "Content-Type: application/json" -X POST 127.0.0.1:5000/get-workflow-templates
```

Response:

```json
{
    "status":"OK",
    "templates":
    {
        "cwl":["annotation","broad"],
        "toil":["musico-api","pakRunner"]
    }
}

```

### Manipulation of the workflow template description

#### Set template description

```bash
curl -X POST http://127.0.0.1:5000/template-description -F "workflow-template=template"  -F "type=cwl"  -F "description=Some description"
```

```json
{
    "success":true
}
```

#### Get template description

```bash
curl http://127.0.0.1:5000/template-description?workflow-template=template 
```

```json
{
    "success":true,
    "description":"Some description"
}
```

#### Update template description

```bash
curl -X PUT http://127.0.0.1:5000/template-description -F "workflow-template=template"   -F "type=cwl"  -F "description=Some description"
```

```json
{
    "success":true
}
```

#### Delete template description

```bash
curl -X DELETE http://127.0.0.1:5000/template-description -F "workflow-template=template"
```

```json
{
    "success":true
}
```


### Create workflow



Parameters:

* `type` - field must be either `cwl` or `toil`
* `workflow-template` - field specifies the template from which the workflow will be created
* `metadata` (optional) - field specifies some description of the workflow that is being created

This request specifies which workflow will be run and uploads two files:

* `yaml` - `.yaml` file that contains input bindings for the specified workflow
* `input_zip` (optional) - `.zip` file containing all the input files for the workflow if neccessary

*Note:*
Yaml file that determines the inputs od the workflow can have additional field `girderIds`. This field is an array consisting of file ids stored on Girder. All the files specified in this field will be downloaded from Girder platform if they are not sent in the `input_zip` field. Header `girder-api-key` containing users api-key is needed in order to download the specified files.

Creating workflow from `toil` template:
```bash
curl -F 'yaml=@mnt/d/inputs.yaml' -F 'input_zip=@mnt/d/inputs.zip' -F 'type=toil' -F 'workflow-template=musico-api' 127.0.0.1:5000/create-workflow

```

Response:

```json
{
    "succcess": true,
    "GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"
}
```


Creating workflow from `cwl` template (this template is located [here](https://github.com/Andreja28/cloud-workflows/tree/master/cwl/unzip-cwl)):
```bash
curl -F 'yaml=@mnt/d/inputs.yaml' -F 'input_zip=@mnt/d/inputs.zip' -F 'type=cwl' -F 'workflow-template=unzip-cwl' 127.0.0.1:5000/create-workflow

```

Response:

```json
{
    "succcess": true,
    "GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d"
}
```

### List workflows

Optional parameters for filtering workflows are:
- *userID* (`userID` is specified in the metadata)
- *type* (cwl or toil)
- *workflow-template*
- *status*

Example below is filtering workflows by the workflow template (in this case `musico-api`)

```bash
curl 127.0.0.1:5000/get-workflows?workflow-template=musico-api
```

Response:

```json
{
    "workflows":[
        {"GUID":"c804a9a7-b41b-4104-b9c9-141ea953020a","status":"NOT_YET_EXECUTED","workflow-template":"musico-api", "metadata":"Some metadata","type":"cwl"},
        {"GUID":"f56c9009-8ad8-4236-b95d-cc6b2d0be0d6","status":"FINISHED_OK","workflow-template":"musico-api", "metadata":"Some metadata", "type":"cwl"},
        {"GUID":"e1810518-f626-44cc-8636-644ee5da799b","status":"FINISHED_OK","workflow-template":"musico-api", "metadata":"Some metadata", "type":"cwl"}
    ]
}
```


### Get workflow info



```bash
curl 127.0.0.1:5000/get-workflow-info?GUID=$GUID
```

Response:

```json
{
    "success":true,
    "workflow":
    {
        "GUID":"d0ecf151-b358-45ad-9392-3fd124605116",
        "metadata":"Some metadata",
        "status":"NOT_YET_EXECUTED",
        "workflow-template":"echo-cwl",
        "type":"cwl"
    }
}
```

List of possible `status` field:

* NOT_YET_EXECUTED
* TERMINATED
* RUNNING
* FINISHED_OK
* FINISHED_ERROR


### Run workflow

This request takes only `GUID` as input:

```bash
curl -d '{"GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/run-workflow
```

Response:

```json
{
    "success": true
}
```

*Note:*
If `girder-api-key` header is specified outputs of the workflow will be uploaded to the users private space on Girder.

### Get status

```bash
curl 127.0.0.1:5000/get-status?GUID=$GUID 
```

Response if the job is still running:

```json
{
    "message":"Of the 44 jobs considered, there are 31 jobs with children, 13 jobs ready to run, 0 zombie jobs, 0 jobs with services, 0 services, and 0 jobs with log files currently in FileJobStore(/home/user/FES-API/running/bc56c810-fc3a-456e-bdb8-5f9c134a03eb).\n",
    "status":"RUNNING",
    "success":true
}

```

Response if the job is finished or if it's not yet run:

```json
{
    "message":"No job store found.\n",
    "status":"FINISHED_OK",
    "success":true
}

```

### Get results

```bash
curl 127.0.0.1:5000/get-results?GUID=$GUID --output file.zip
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9350k  100 9350k    0     0  84.8M      0 --:--:-- --:--:-- --:--:-- 85.3M

```

### Download single output file

```bash
curl 127.0.0.1:5000/get-output-file?GUID=$GUID --output file
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9350k  100 9350k    0     0  84.8M      0 --:--:-- --:--:-- --:--:-- 85.3M

```

### Get output metadata

Request:

```bash 
curl 127.0.0.1:5000/get-output-metadata?GUID=$GUID 
```


Response:
```json
    {
        "success": true,
        "workflow": 
        {
            "GUID": "$GUID",
            "creationDate": "2021-09-22T14:25:48.277536",
            "downloadOutput": "http://127.0.0.1:5000/get-results?GUID=$GUID",
            "metadata": null,
            "outputs": 
            {
                "ext1": [
                    {
                        "filename": "file1.ext1",
                        "link": "http://127.0.0.1:5000/get-output-file?GUID=$GUID&filepath=file1.ext1"
                    },
                    {
                        "filename": "file2.ext1",
                        "link": "http://127.0.0.1:5000/get-output-file?GUID=$GUID&filepath=file2.ext1"
                    }
                ],
                "ext2": [
                    {
                        "filename": "file1.ext2",
                        "link": "http://127.0.0.1:5000/get-output-file?GUID=$GUID&filepath=file1.ext2"
                    },
                    {
                        "filename": "file2.ext2",
                        "link": "http://127.0.0.1:5000/get-output-file?GUID=$GUID&filepath=file2.ext2"
                    }
                ]
            }
        }
    }
```


### Upload results to Girder

This request takes only `GUID` as input:

```bash
curl -d '{"GUID":"14822ea8-5c10-4161-b51c-7ef9c4b6ed0f"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/upload-results
```

```json
{
    "uploadedFolder":{
        "_accessLevel":2,
        "_id":"5f68934ca4c3269067f6a36d",
        "_modelType":"folder",
        "baseParentId":"5f589bfba4c3269067f69f20",
        "baseParentType":"user",
        "created":"2020-09-21T11:49:32.359000+00:00",
        "creatorId":"5f589bfba4c3269067f69f20",
        "description":"",
        "meta":{},
        "name":"14822ea8-5c10-4161-b51c-7ef9c4b6ed0f",
        "parentCollection":"folder",
        "parentId":"5f64c342a4c3269067f6a07c",
        "public":true,
        "size":920914,
        "updated":"2020-09-21T11:49:32.359000+00:00"
    }
}
```

### Get log file

If the log file is created (workflow has been run):

```bash
curl 127.0.0.1:5000/get-log?GUID=$GUID --output log.txt
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9350k  100 9350k    0     0  84.8M      0 --:--:-- --:--:-- --:--:-- 85.3M

```

### Download workflow

Downloads `zip` file that containes the entire workflow (**workflow-template** from which the workflow is created, **inputs** for the workflow and **zipped results** if the workflow has already been run). Upon download user will be able to run workflow locally, either manually or using the bash script provided in the downloaded `zip`.


```bash
curl 127.0.0.1:5000/download-workflow?GUID=$GUID --output workflow.zip
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   610  100   610    0     0   148k      0 --:--:-- --:--:-- --:--:--  148k


```

### Stop workflow

Terminates execution of a running workflow.

```bash
curl -d '{"GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/stop-workflow
```

Response:

```json
{
    "success": true,
    "message": "Workflow terminated."
}
```

### Delete workflow

Deletes all files of the workflow (only if the workflow is not active).

```bash
curl -d '{"GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/delete-workflow
```

Response:

```json
{
    "success": true
}
```


