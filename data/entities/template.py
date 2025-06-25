from api.database.models import Template
from api.database.repositories import TemplateRepository
import os
from config import *

class TemplateEntity:
    
    def __init__(self, path: str = None, name: str = None, description: str = None, template: Template = None):
        if template is not None:
            # Initialize from a Template object
            self.name = template.name
            self.description = template.description
            self.path = TemplateEntity.template_path(template)
        elif path and name and description:
            # Initialize from path, name, and description
            self.path = path
            self.name = name
            self.description = description
        else:
            raise ValueError("Invalid arguments provided to TemplateEntity")


    @classmethod
    def get_templates(cls, template_objects):
        return [
            cls(
                path=os.path.join(TEMPLATES_DIR, folder),
                name=folder,
                description=next((template.description for template in template_objects if template.name == folder), "")
            )
            for folder in os.listdir(TEMPLATES_DIR)
            if os.path.isdir(os.path.join(TEMPLATES_DIR, folder)) and any(template.name == folder for template in template_objects)
        ]

    

    @classmethod
    def template_path(cls, template: Template):
        return f"{TEMPLATES_DIR}/{template.name}/workflow.cwl"