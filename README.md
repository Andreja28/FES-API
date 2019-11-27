# FES-API

## Installation

```bash
#Python 2.7
sudo apt-get install python-virtualenv
```

```bash
cd FES-API
python2 -m virtualenv venv
. venv/bin/activate
pip install Flask
export FLASK_APP=hello.py
flask run
```

The file `config.py` contains variables `CWL` (path to folder containing CWL workflows), `TOIL` (path to folder containing Toil workflows), `RESULTS` (path to folder where the workflow results will be stored) and `RUNNING_WORKFLOWS` (path to folder where the temoporary workflow job stores will be located).



## Examples

### Echo

```bash
curl -d '{"workflow":"another-cwl", "type":"cwl"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/echo
```

Response:

```json
{
    "status":"OK",
    "your_request":
    {
        "type":"cwl",
        "workflow":"another-cwl"
    }
}

```


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


### Create workflow



Parameters:

* `type` - field must be either `cwl` or `toil`
* `workflow-template` - field specifies the template from which the workflow will be created
* `metadata` (optional) - field specifies some description of the workflow that is being created

This request specifies which workflow will be run and uploads two files:

* `yaml` - `.yaml` file that contains input bindings for the specified workflow
* `input_zip` (optional) - `.zip` file containing all the input files for the workflow if neccessary

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

### List of all workflows

```bash
curl 127.0.0.1:5000/get-workflows
```

Response:

```json
{
    "workflows":[
        {"GUID":"c804a9a7-b41b-4104-b9c9-141ea953020a","status":"not run","workflow-template":"musico-api", "metadata":"Some metadata"},
        {"GUID":"f56c9009-8ad8-4236-b95d-cc6b2d0be0d6","status":"finished","workflow-template":"musico-api", "metadata":"Some metadata"},
        {"GUID":"e1810518-f626-44cc-8636-644ee5da799b","status":"finished","workflow-template":"musico-api", "metadata":"Some metadata"}
    ]
}
```

### Get workflow info



```bash
curl 127.0.0.1:5000/get-workflow?GUID=$GUID
```

Response:

```json
{
    "success":true,
    "workflow":
    {
        "GUID":"d0ecf151-b358-45ad-9392-3fd124605116",
        "metadata":"Some metadata",
        "status":"not run or doesn't exist",
        "workflow-template":"echo-cwl"
    }
}
```


### Run workflow

This request takes 3 fields as an input: 
* `workflow` - specifies the name of the workflow
* `type` - specifies the type of the workflow (either `cwl` or `toil`)
* `timelimit` - specifies maximum execution time of the workflow in seconds. If the workflow exceeds this time limit it will be shutdown.

```bash
curl -d '{"GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64", "timelimit":3000}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/run-workflow
```

Response:

```json
{
    "success": true
}
```

### Get status

```bash
curl 127.0.0.1:5000/get-status?GUID=$GUID 
```

Response if the job is still running:

```json
{
    "message":"Of the 44 jobs considered, there are 31 jobs with children, 13 jobs ready to run, 0 zombie jobs, 0 jobs with services, 0 services, and 0 jobs with log files currently in FileJobStore(/home/user/FES-API/running/bc56c810-fc3a-456e-bdb8-5f9c134a03eb).\n",
    "success":true
}

```

Response if the job is finished:

```json
{
    "message":"No job store found.\n",
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

### Download workflow

Downloads `zip` file that containes the entire workflow (**workflow-template** from which the workflow is created, **inputs** for the workflow and **zipped results** if the workflow has already been run). Upon download user will be able to run workflow locally, either manually or using the script provided in the downloaded `zip`.


```bash
curl 127.0.0.1:5000/download-workflow?GUID=$GUID --output file.zip
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


