from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from api.database import Base


class Template(Base):
    __tablename__ = 'templates'

    name = Column(String(50), primary_key=True)
    description = Column(Text)

    # Relationship to Workflow
    workflows = relationship("Workflow", back_populates="template", lazy='joined')

