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

### Run workflow

This request takes 3 fields as an input: 
* `workflow` - specifies thename of the workflow
* `type` - specifies the type of the workflow (either `cwl` or `toil`)
* `timelimit` - specifies max time the workflow is expected to be running. If a workflow exceeds this timelimit it will be shutdown.

```bash
curl -d '{"workflow":"pakRunner", "type":"toil", "timelimit":60}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/run-workflow
```

Response:

```json
{
    "status":"OK",
    "workflow_id":"3794dfa3-48c3-48f8-ab50-0e9fc014cd64"
}
```

### Get status

```bash
curl 127.0.0.1:5000/get-status?workflow_id=$WORKFLOW_ID 
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
curl 127.0.0.1:5000/get-results?workflow_id=$WORKFLOW_ID --output file.zip
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9350k  100 9350k    0     0  84.8M      0 --:--:-- --:--:-- --:--:-- 85.3M

```



