DATABASE_URL = "sqlite:///data/workflows.db"
TEMPLATES_DIR = "data/templates"
WORKFLOWS_DIR = "data/workflows"
LOGS_DIR = "data/workflows/logs"
JOBSTORE_DIR = "data/workflows/running"
INPUTS_DIR = "data/workflows/inputs"
RESULTS_DIR = "data/workflows/results"

EXTENSIONS = {
    "video" : [".ogv"],
    "data" : [".csv", ".txt"],
    "model" : [".vtk"]
}

__all__ = [
    "DATABASE_URL",
    "TEMPLATES_DIR",
    "WORKFLOWS_DIR",
    "LOGS_DIR",
    "JOBSTORE_DIR",
    "INPUTS_DIR",
    "RESULTS_DIR",
    "EXTENSIONS",
]
