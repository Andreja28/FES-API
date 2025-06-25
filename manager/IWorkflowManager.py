from abc import ABC,ABCMeta, abstractmethod

from data.entities import WorkflowEntity as Workflow
from threading import Lock

class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            if not hasattr(cls, "_lock"):
                cls._lock = Lock()
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class IWorkflowManager(ABC, metaclass=SingletonMeta):

    @abstractmethod
    def get_workflow(self, workflow: Workflow):
        pass

    @abstractmethod
    def get_thread(self, workflow: Workflow):
        pass

    @abstractmethod
    def run(self, workflow: Workflow, params: dict = None):
        pass

    @abstractmethod
    def terminate(self, workflow: Workflow):
        pass

    