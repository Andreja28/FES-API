
from .IWorkflowManager import IWorkflowManager
from .WorkflowManager import WorkflowManager as wfm

WorkflowManager = wfm.get_manager("CwlTool")

__all__ = [
    "IWorkflowManager",
    "WorkflowManager"
]