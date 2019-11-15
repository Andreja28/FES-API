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


### List of all workflows

```bash
curl -H "Content-Type: application/json" -X POST 127.0.0.1:5000/get-workflows
```

Response:

```json
{
    "status":"OK",
    "workflows":
    {
        "cwl":["annotation","broad"],
        "toil":["musico-api","pakRunner"]
    }
}

```


### Create workflow

This request specifies which workflow will be run and uploads two files (`.zip` containing all the input files for the workflow and `.yaml` file).

```bash
curl -F 'yaml=@mnt/d/inputs.yaml' -F 'input_zip=@mnt/d/inputs.zip' -F 'type=toil' -F 'workflow=musico-api' 127.0.0.1:5000/create-workflow

```

Response:

```json
{
    "succcess": true,
    "GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"
}
```


### List of all created workflows

```bash
curl 127.0.0.1:5000/get-created-workflows
```

Response:

```json
{
    "workflows":[
        {"GUID":"c804a9a7-b41b-4104-b9c9-141ea953020a","status":"not run","workflow":"musico-api"},
        {"GUID":"f56c9009-8ad8-4236-b95d-cc6b2d0be0d6","status":"finished","workflow":"musico-api"},
        {"GUID":"e1810518-f626-44cc-8636-644ee5da799b","status":"finished","workflow":"musico-api"}
    ]
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
    "status":"OK",
    "GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"
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

Deletes all files of the created workflow (only if the workflow is not active).

```bash
curl -d '{"GUID":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/delete-workflow
```

Response:

```json
{
    "success": true
}
```
