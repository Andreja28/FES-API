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

File config.py contains variables `CWL` (path to folder containing CWL workflows), `TOIL` (path to folder containing Toil workflows), `RESULTS` (path to folder where the workflow results will be stored) and `RUNNING_WORKFLOWS` (path to folder where the temoporary workflow job stores will be located).



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

```bash
curl -d '{"workflow":"broad", "type":"cwl"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/run-workflow
```

Response:

```json
{
    "status":"OK",
    "workflow_id":"1571847979.94"
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