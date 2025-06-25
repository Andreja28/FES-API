from fastapi import UploadFile
import data.utils as utils
from data.entities import TemplateEntity
from api.database.repositories import WorkflowRepository
from api.database.models import Workflow
from enum import Enum
from exceptions.api import YamlValidationException

class ExecutionStatus(Enum):
    NOT_YET_EXECUTED = "NOT_YET_EXECUTED"
    TERMINATED = "TERMINATED"
    RUNNING = "RUNNING"
    FINISHED_OK = "FINISHED_OK"
    FINISHED_ERROR = "FINISHED_ERROR"

class WorkflowEntity:
    
    def __init__(self, workflow:Workflow = None, template: TemplateEntity = None, yaml: UploadFile =None, inputs: list[UploadFile] = None, metadata: str = None):
        if workflow is None:

            self.template = template
            self.GUID = utils.generate_GUID()
            self.workdir = utils.get_workflow_dirs(self.GUID)
            self.PID = None

            yaml = utils.save_file(yaml, f"{self.workdir['inputs']}/inputs.yaml")
            for file in inputs:
                utils.save_file(file, f"{self.workdir['inputs']}/{file.filename}")
                    
            
            missing = utils.validate_inputs(yaml, self.workdir['inputs'])
            if missing.__len__() > 0:
                utils.delete_workdir(self.GUID)
                raise YamlValidationException(missing = missing)

            self.status = ExecutionStatus.NOT_YET_EXECUTED

            self.metadata = metadata

            try:
                workflow = WorkflowRepository.create_workflow(self.GUID, self.template.name, metadata)
                self.timestamp = workflow.timestamp
                utils.zip_folder(self.workdir['inputs'], self.workdir['inputs'])
            except Exception as e:
                raise e
        else:
            self.GUID = workflow.GUID
            self.template = TemplateEntity(template=workflow.template)
            self.workdir = utils.get_workflow_dirs(self.GUID)
            self.timestamp = workflow.timestamp
            self.status = ExecutionStatus(workflow.status)
            self.metadata = workflow.meta
            self.PID = workflow.PID
            # self.status = ExecutionStatus(workflow.status) if workflow.status else ExecutionStatus.NOT_YET_EXECUTED
