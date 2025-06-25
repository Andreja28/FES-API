guid_422_response = {
    "description": "Invalid GUID format",
    "content": {
        "application/json": {
            "example": {"detail": "Invalid GUID format"}
        }
    }
}

get_workflow_inputs_responses = {
    200: {
        "description": "Download workflow inputs (zip or single file)",
        "content": {
            "application/octet-stream": {
                "example": b"ZIP or file content"
            }
        }
    },
    404: {
        "description": "File or workflow not found",
        "content": {
            "application/json": {
                "example": {"message": "File 'input.txt' does not exist in the inputs directory of the workflow with GUID: '1234'."}
            }
        }
    },
    422: guid_422_response,
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

get_workflow_log_responses = {
    200: {
        "description": "Download workflow log file",
        "content": {
            "application/octet-stream": {
                "example": b"Log file content"
            }
        }
    },
    404: {
        "description": "Workflow not found or not executed yet",
        "content": {
            "application/json": {
                "example": {"message": "Workflow with GUID: '1234' has not been executed yet."}
            }
        }
    },
    422: guid_422_response,
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

get_download_metadata_responses = {
    200: {
        "description": "Workflow files metadata",
        "content": {
            "application/json": {
                "example": {
                    "guid": "1234",
                    "files": [
                        {"name": "inputs.yaml", "size": 1234},
                        {"name": "results.csv", "size": 5678}
                    ],
                    "tree": {}
                }
            }
        }
    },
    404: {
        "description": "Workflow not found",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow not found"}
            }
        }
    },
    422: guid_422_response,
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

get_workflow_results_responses = {
    200: {
        "description": "Download workflow results (zip or single file)",
        "content": {
            "application/octet-stream": {
                "example": b"ZIP or file content"
            }
        }
    },
    404: {
        "description": "File or workflow not found",
        "content": {
            "application/json": {
                "example": {"message": "File 'result.txt' does not exist in the results directory of the workflow with GUID: '1234'."}
            }
        }
    },
    409: {
        "description": "Workflow is not finished successfully",
        "content": {
            "application/json": {
                "example": {"message": "Workflow is not finished successfully."}
            }
        }
    },
    422: guid_422_response,
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

download_workflow_responses = {
    200: {
        "description": "Download the entire workflow as a zip file",
        "content": {
            "application/octet-stream": {
                "example": b"ZIP file content"
            }
        }
    },
    404: {
        "description": "Workflow not found",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow not found"}
            }
        }
    },
    422: guid_422_response,
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}