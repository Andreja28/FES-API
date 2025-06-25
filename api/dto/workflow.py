from pydantic import BaseModel
from data.entities import WorkflowEntity
from api.dto import TemplateDTO
from data.entities import ExecutionStatus
from datetime import datetime

class WorkflowDTO(BaseModel):
    GUID: str
    template: TemplateDTO
    status: ExecutionStatus
    metadata: str
    timestamp: datetime

    @classmethod
    def from_entity(cls, workflow_entity: WorkflowEntity):
        return cls(
            GUID=workflow_entity.GUID,
            template=TemplateDTO.from_entity(workflow_entity.template),
            status=workflow_entity.status,
            metadata=workflow_entity.metadata if workflow_entity.metadata else "",
            timestamp=datetime.fromisoformat(workflow_entity.timestamp)
        )