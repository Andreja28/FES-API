# Step-by-Step Tutorial: Running the `unzip-cwl` Workflow via API

This guide shows how to run the `unzip-cwl` workflow using the API endpoints described in the `README.md`.
Input yaml and input file for the worklfow are located in the `./data/templates/unzip-cwl/` directtpry
---

## 1. Start the API Server

Make sure your FastAPI server is running:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

---


## 2. Create a Workflow Instance

Assuming you have:
- A YAML file describing the workflow inputs (e.g., `inputs.yaml`)
- One input file (e.g., `inputs.tar.gz`)

Run:

```bash
curl -X POST "http://localhost:8080/api/workflows/create" \
  -F "template=unzip-cwl" \
  -F "yaml=@inputs.yaml" \
  -F "inputs=@inputs.tar.gz"
```

**Response Example:**
```json
{
  "GUID": "your-workflow-guid",
  "template": {
    "name": "unzip-cwl",
    "description": "Unzips a CWL archive and processes its contents"
  },
  "status": "NOT_YET_EXECUTED",
  "metadata": ""
}
```

Save the `GUID` from the response for the next steps.

---

## 3. Start the Workflow

```bash
curl -X POST "http://localhost:8080/api/workflows/run" \
  -F "GUID=your-workflow-guid"
```

---

## 4. Check Workflow Status

You can check the status at any time:

```bash
curl "http://localhost:8080/api/workflows/info?guid=your-workflow-guid"
```

---

## 5. Download Workflow Results

Once the workflow status is `FINISHED_OK`, download the results:

```bash
curl -o results.zip "http://localhost:8080/api/workflows/download/results?guid=your-workflow-guid"
```

*This will save the results as `results.zip` in your current directory.*

---

## 6. (Optional) Stop the Workflow

If you need to stop a running workflow:

```bash
curl -X POST "http://localhost:8080/api/workflows/stop" \
  -F "GUID=your-workflow-guid"
```

---

## 7. (Optional) Delete the Workflow

When finished, you can delete the workflow:

```bash
curl -X DELETE "http://localhost:8080/api/workflows/" \
  -F "GUID=your-workflow-guid"
```

---

## Notes

- Replace `your-workflow-guid` with the actual GUID returned from the create step.
- All endpoints return JSON responses unless downloading results.
- For more details, see the Swagger UI at [http://localhost:8080/docs](http://localhost:8080/docs)