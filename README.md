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



## Examples

### Echo

```bash
curl -d '{"workflow":"another-cwl", "cwl_toil":"cwl"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/echo
```

Response:

```json
{
    "status":"OK",
    "your_request":
    {
        "cwl_toil":"cwl",
        "workflow":"another-cwl"
    }
}

```


### List of all workflows

```bash
curl -H "Content-Type: application/json" -X POST 127.0.0.1:5000/get_all_workflows
```

Response:

```json
{
    "status":"OK",
    "workflows":
    {
        "cwl":["another-cwl","import_cwl"],
        "toil":["musico-api","pakRunner"]
    }
}

```

### Run workflow

```bash
curl -d '{"workflow":"another-cwl", "cwl_toil":"cwl"}' -H "Content-Type:application/json" -X POST 127.0.0.1:5000/run_workflow
```

Response:

```json
{
    "status":"OK",
    "workflow_id":"1571847979.94"
}

```