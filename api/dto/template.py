from pydantic import BaseModel
from data.entities import TemplateEntity
from api.database.models import Template as TemplateModel

class TemplateDTO(BaseModel):
    
    name: str
    description: str

    @classmethod
    def from_entity(cls, template_entity: TemplateEntity):
        return cls(
            name=template_entity.name,
            description=template_entity.description
        )
    @classmethod
    def from_model(cls, template_model: TemplateModel):
        return cls(
            name=template_model.name,
            description=template_model.description
        )