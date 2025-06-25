get_templates_responses = {
    200: {
        "description": "List of templates",
        "content": {
            "application/json": {
                "example": [
                    {
                        "name": "template1",
                        "description": "A sample template"
                    }
                ]
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

get_template_responses = {
    200: {
        "description": "Template details",
        "content": {
            "application/json": {
                "example": {
                    "name": "template1",
                    "description": "A sample template"
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
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

set_template_description_responses = {
    200: {
        "description": "Template description set",
        "content": {
            "application/json": {
                "example": {"message": "Template description set successfully."}
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
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

delete_template_description_responses = {
    200: {
        "description": "Template description deleted",
        "content": {
            "application/json": {
                "example": {"message": "Template description deleted successfully."}
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
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}
