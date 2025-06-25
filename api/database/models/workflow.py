import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.database import Base


class Workflow(Base):
    __tablename__ = 'workflows'

    GUID = Column(String(36), primary_key=True)
    template_name = Column('template', ForeignKey('templates.name'), nullable=False)  # Foreign key to templates.name
    PID = Column(Integer, default = None, nullable=True)
    status = Column(String(50), default="NOT_YET_EXECUTED", nullable=False)
    meta = Column('metadata', Text, default= None, nullable=True)
    timestamp = Column(String(50), default=datetime.now().isoformat("T"), nullable=False)
    # Relationship to Template
    template = relationship("Template", back_populates="workflows", lazy='joined')