from pydantic import BaseModel
from data.entities import WorkflowEntity
from api.dto import TemplateDTO
from data.entities import ExecutionStatus

class FilesMetadataDTO(BaseModel):
    GUID: str
    template: TemplateDTO
    status: ExecutionStatus
    downloadInputs: str = None
    inputs: dict= None
    downloadResults: str = None
    results: dict = None
    log: str = None
    downloadWorkflow: str = None

    @classmethod
    def from_entity(cls, workflow_entity: WorkflowEntity):
        return cls(
            GUID=workflow_entity.GUID,
            template=TemplateDTO.from_entity(workflow_entity.template),
            status=workflow_entity.status,
            metadata=workflow_entity.metadata if workflow_entity.metadata else "",
            
        )
    
    def add_tree(self, base_url, tree: dict):
        for key, files in tree['inputs'].items():
            for file in files:
                file['link'] = f"{base_url}api/workflows/download/inputs?guid={self.GUID}&file={file['filename']}"
        
        for key, files in tree['results'].items():
            for file in files:
                file['link'] = f"{base_url}api/workflows/download/results?guid={self.GUID}&file={file['filename']}"
        
        self.downloadInputs = f"{base_url}api/workflows/download/inputs?guid={self.GUID}"
        self.downloadResults = f"{base_url}api/workflows/download/results?guid={self.GUID}"
        
        self.inputs = tree['inputs']
        self.results = tree['results']
        self.log = f"{base_url}api/workflows/download/log?guid={self.GUID}"