# User scenario

In order to create a workflow user needs to specify workflow template form which the workflow will be created.
List of all existing templates can be seen with the following request:

### List of all workflow templates

```bash
curl -H "Content-Type: application/json" -X POST cluster2.bioirc.ac.rs:5000/get-workflow-templates
```

Response:

```json
{
    "status":"OK",
    "templates":
    {
        "cwl":["annotation","broad","c-cwl"],
        "toil":["musico-api","pakRunner"]
    }
}

```

After selecting workflow template (with corresponding type - `cwl` or `toil`) user can create a workflow (providing `.yaml` for the input bindings and `.zip` with archived input files if needed). This can be accomplished with the following request:

### Create workflow

Parameters:

* `type` - field must be either `cwl` or `toil`
* `workflow-template` - field specifies the template from which the workflow will be created
* `metadata` (optional) - field specifies some description of the workflow that is being created

This request specifies which workflow will be run and uploads two files:

* `yaml` - `.yaml` file that contains input bindings for the specified workflow
* `input_zip` (optional) - `.zip` file containing all the input files for the workflow if neccessary




Creating workflow from `c-cwl` template (this template is located [here](https://github.com/Andreja28/cloud-workflows/tree/master/cwl/c-cwl)). This workflow has two nodes (workflow requires two files for it to run - `pi.c` and `in.txt` and they need to be zipped). One for compiling the code and the other for running it:

```bash
curl -F 'yaml=@mnt/d/inputs.yaml' -F 'input_zip=@mnt/d/inputs.zip' -F 'type=cwl' -F 'workflow-template=c-cwl' -F 'metadata=Some metadata' cluster2.bioirc.ac.rs:5000/create-workflow

```

Response:

```json
{
    "succcess": true,
    "GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d"
}
```

Once the workflow is created user can get some general info about the workflow (whether the workflow is running, is finished, is not yet run, etc.) providing correcponding `GUID`:

### Get workflow info



```bash
curl cluster2.bioirc.ac.rs:5000/get-workflow-info?GUID=94506c1d-57cf-4268-83c1-f80b0c7e6c1d
```

Response:

```json
{
    "success":true,
    "workflow":
    {
        "GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d",
        "metadata":"Some metadata",
        "status":"not run or doesn't exist",
        "workflow-template":"c-cwl"
    }
}
```


It is time for running the workflow:

### Run workflow

This request takes only `GUID` as input:

```bash
curl -d '{"GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d"}' -H "Content-Type:application/json" -X POST cluster2.bioirc.ac.rs:5000/run-workflow
```

Response:

```json
{
    "success": true
}
```


If the workflow is running it is possible to get it's status with the following request:

### Get status

```bash
curl cluster2.bioirc.ac.rs:5000/get-status?GUID=94506c1d-57cf-4268-83c1-f80b0c7e6c1d
```

Response if the job is still running:

```json
{
    "message":"Of the 2 jobs considered, there are 1 jobs with children, 1 jobs ready to run, 0 zombie jobs, 0 jobs with services, 0 services, and 0 jobs with log files currently in FileJobStore(/home/user/FES-API/running/94506c1d-57cf-4268-83c1-f80b0c7e6c1d).\n",
    "success":true
}

```

Response if the job is finished or if it's not yet run:

```json
{
    "message":"No job store found.\n",
    "success":true
}

```

If for some reason it is required to stop the running workflow it is possible with the following request:


### Stop workflow

Terminates execution of a running workflow.

```bash
curl -d '{"GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d"}' -H "Content-Type:application/json" -X POST cluster2.bioirc.ac.rs:5000/stop-workflow
```

Response:

```json
{
    "success": true,
    "message": "Workflow terminated."
}
```

When the workflow is finished successfully user can download results from the workflow:

### Get results

```bash
curl cluster2.bioirc.ac.rs:5000/get-results?GUID=94506c1d-57cf-4268-83c1-f80b0c7e6c1d --output file.zip
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 9350k  100 9350k    0     0  84.8M      0 --:--:-- --:--:-- --:--:-- 85.3M

```

User can also download the whole workflow including the results if they exist:

### Download workflow

Downloads `zip` file that containes the entire workflow (**workflow-template** from which the workflow is created, **inputs** for the workflow and **zipped results** if the workflow has already been run). Upon download user will be able to run workflow locally, either manually or using the bash script provided in the downloaded `zip`.


```bash
curl cluster2.bioirc.ac.rs:5000/download-workflow?GUID=94506c1d-57cf-4268-83c1-f80b0c7e6c1d --output workflow.zip
```

Response:

```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   610  100   610    0     0   148k      0 --:--:-- --:--:-- --:--:--  148k


```

If the workflow is no longer needed and will no longer be used, user can delete the entire workflow:

### Delete workflow

Deletes all files of the workflow (only if the workflow is not active).

```bash
curl -d '{"GUID":"94506c1d-57cf-4268-83c1-f80b0c7e6c1d"}' -H "Content-Type:application/json" -X POST cluster2.bioirc.ac.rs:5000/delete-workflow
```

Response:

```json
{
    "success": true
}
```