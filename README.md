# FES-API

## Installation

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8080
```

## API Documentation

Interactive API docs are available at:
- Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)
- ReDoc: [http://localhost:8080/redoc](http://localhost:8080/redoc)

---


## Templates API

### List Templates

**GET** `/templates/`

**cURL Example:**
```bash
curl "http://localhost:8080/templates/"
```

**Response Example (200):**
```json
[
  {
    "name": "template1",
    "description": "A sample template"
  }
]
```

---

### Get Template

**GET** `/templates/{template}`

**cURL Example:**
```bash
curl "http://localhost:8080/templates/template1"
```

**Response Example (200):**
```json
{
  "name": "template1",
  "description": "A sample template"
}
```

---

### Set Template Description

**POST** `/templates/description`

- **Form fields:**
  - `template` (str, required)
  - `description` (str, required)

**cURL Example:**
```bash
curl -X POST "http://localhost:8080/templates/description" \
  -F "template=template1" \
  -F "description=New description"
```

**Response Example (200):**
```json
{
  "message": "Template description set successfully."
}
```

---

### Delete Template Description

**DELETE** `/templates/description?template={template}`

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8080/templates/description?template=template1"
```

**Response Example (200):**
```json
{
  "message": "Template description deleted successfully."
}
```

---


## Workflows API

### Create Workflow

**POST** `/workflows/create`

- **Form fields:**
  - `template` (str, required): Template name
  - `yaml` (file, required): YAML file
  - `inputs` (file[], optional): Input files

**cURL Example:**
```bash
curl -X POST "http://localhost:8080/workflows/create" \
  -F "template=template1" \
  -F "yaml=@workflow.yaml" \
  -F "inputs=@input1.txt" \
  -F "inputs=@input2.txt"
```

**Response Example (200):**
```json
{
  "GUID": "123e4567-e89b-12d3-a456-426614174000",
  "template": {
    "name": "template1",
    "description": "A sample template"
  },
  "status": "NOT_YET_EXECUTED",
  "metadata": ""
}
```

---

### List Workflows

**GET** `/workflows/`

- **Query parameters (optional):**
  - `template` (str)
  - `status` (str)
  - `userID` (str)

**cURL Example:**
```bash
curl "http://localhost:8080/workflows/?template=template1&status=NOT_YET_EXECUTED&userID=someuser"
```

**Response Example (200):**
```json
[
  {
    "GUID": "123e4567-e89b-12d3-a456-426614174000",
    "template": {
      "name": "template1",
      "description": "A sample template"
    },
    "status": "NOT_YET_EXECUTED",
    "metadata": "",
    "timestamp": "2025-06-08T11:45:05.476803"
  }
]
```

---

### Get Workflow Info

**GET** `/workflows/info?guid={GUID}`

**cURL Example:**
```bash
curl "http://localhost:8080/workflows/info?guid=123e4567-e89b-12d3-a456-426614174000"
```

**Response Example (200):**
```json
{
  "GUID": "123e4567-e89b-12d3-a456-426614174000",
  "template": {
    "name": "template1",
    "description": "A sample template"
  },
  "status": "RUNNING",
  "metadata": "",
  "timestamp": "2025-06-08T11:45:05.476803"
}
```

---

### Run Workflow

**POST** `/workflows/run`

- **Form fields:**
  - `GUID` (str, required)

**cURL Example:**
```bash
curl -X POST "http://localhost:8080/workflows/run" \
  -F "GUID=123e4567-e89b-12d3-a456-426614174000"
```

**Response Example (200):**
```json
{
  "message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been started successfully."
}
```

---

### Stop Workflow

**POST** `/workflows/stop`

- **Form fields:**
  - `GUID` (str, required)

**cURL Example:**
```bash
curl -X POST "http://localhost:8080/workflows/stop" \
  -F "GUID=123e4567-e89b-12d3-a456-426614174000"
```

**Response Example (200):**
```json
{
  "message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been terminated successfully."
}
```

---

### Delete Workflow

**DELETE** `/workflows/`

- **Form fields:**
  - `GUID` (str, required)

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8080/workflows/" \
  -F "GUID=123e4567-e89b-12d3-a456-426614174000"
```

**Response Example (200):**
```json
{
  "message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been deleted successfully."
}
```

---

## Error Responses

Most endpoints may return:
- `404 Not Found` if the resource does not exist
- `422 Unprocessable Entity` for validation errors
- `500 Internal Server Error` for unexpected issues

See `/docs` for detailed error examples.

---

## Notes

- All endpoints return JSON.
- For full details and try-it-out, use the Swagger UI at `/docs`.

