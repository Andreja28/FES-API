
from .IWorkflowManager import IWorkflowManager
from exceptions.manager import UnknownManagerException

class WorkflowManager():
    @staticmethod
    #type should be in some config file
    def get_manager(manager_type: str = "CwlTool") -> IWorkflowManager:
        if manager_type == "CwlTool":
            from manager.implementations.CwlToolManager import CwlToolManager
            return CwlToolManager()
        else:
            raise UnknownManagerException(f"Unknown workflow manager type: {manager_type}")