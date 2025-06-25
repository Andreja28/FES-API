guid_422_response = {
    "description": "Invalid GUID format",
    "content": {
        "application/json": {
            "example": {"detail": "Invalid GUID format"}
        }
    }
}

create_workflow_responses = {
    200: {
        "description": "Workflow created successfully",
        "content": {
            "application/json": {
                "example": {
                    "GUID": "123e4567-e89b-12d3-a456-426614174000",
                    "template": {
                        "name": "template1",
                        "description": "A sample template"
                    },
                    "status": "NOT_YET_EXECUTED",
                    "metadata": ""
                }
            }
        }
    },
    404: {
        "description": "Template not found",
        "content": {
            "application/json": {
                "example": {"detail": "Template not found"}
            }
        }
    },
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_guid": guid_422_response["content"]["application/json"]["example"],
                    "invalid_yaml": {"detail": "Invalid YAML or input files"}
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

# For all other responses, add 422 for invalid GUID

list_workflows_responses = {
    200: {
        "description": "List of workflows",
        "content": {
            "application/json": {
                "example": [
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

get_workflow_info_responses = {
    200: {
        "description": "Workflow info",
        "content": {
            "application/json": {
                "example": {
                    "GUID": "123e4567-e89b-12d3-a456-426614174000",
                    "template": {
                        "name": "template1",
                        "description": "A sample template"
                    },
                    "status": "RUNNING",
                    "metadata": "",
                    "timestamp": "2025-06-08T11:45:05.476803"
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

run_workflow_responses = {
    200: {
        "description": "Workflow started successfully",
        "content": {
            "application/json": {
                "example": {"message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been started successfully."}
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
    409: {
        "description": "Workflow already run or not allowed",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow has already been run."}
            }
        }
    },
    423: {
        "description": "Workflow is locked (already running)",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow is currently being run by another thread."}
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

stop_workflow_responses = {
    200: {
        "description": "Workflow terminated successfully",
        "content": {
            "application/json": {
                "example": {"message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been terminated successfully."}
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
    409: {
        "description": "Workflow not running",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow is not running."}
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

delete_workflow_responses = {
    200: {
        "description": "Workflow deleted successfully",
        "content": {
            "application/json": {
                "example": {"message": "Workflow with GUID: 123e4567-e89b-12d3-a456-426614174000 has been deleted successfully."}
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
    423: {
        "description": "Workflow is locked (running)",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow is currently being run by another thread."}
            }
        }
    },
    409: {
        "description": "Workflow already run or not allowed",
        "content": {
            "application/json": {
                "example": {"detail": "Workflow has already been run."}
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