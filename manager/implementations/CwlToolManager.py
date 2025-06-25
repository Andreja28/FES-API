from api.database.repositories.workflow import WorkflowRepository
from data.entities.workflow import ExecutionStatus
from exceptions.api.database import NotFoundException, DatabaseException
from manager import IWorkflowManager
from data.entities import WorkflowEntity
from manager.threads import WorkflowThread
import threading
import os, signal
from exceptions.manager import *

class CwlToolManager(IWorkflowManager):

    def __init__(self):
        self.threads = []
        self._run_lock = threading.Lock()
        self._guid_locks = dict()
        

    @staticmethod
    def build_command(workflow_path: str, inputs_path:str):
        yaml_path = os.path.abspath(f"{inputs_path}/inputs.yaml") 
        command = f"cwltool {os.path.abspath(workflow_path)} {os.path.abspath(yaml_path)}"
        return command

    def get_workflow(self, GUID: str):
        for thread in self.threads:
            if thread.workflow.GUID == GUID:
                return thread.workflow
        return None
    
    def get_thread(self, GUID: str):
        for thread in self.threads:
            if thread.workflow.GUID == GUID:
                return thread
        return None

    def run(self, GUID: str, params: dict = None):
        with self._run_lock:
            if GUID in self._guid_locks:
                raise RunningException(f"Workflow with GUID: '{GUID}' is currently being run by another thread.")
            self._guid_locks[GUID] = GUID

        try:
            workflow = WorkflowEntity(WorkflowRepository.get_workflow(GUID))
        except NotFoundException as e:
            raise e
        except DatabaseException as e:
            raise e
        
        if workflow.status == ExecutionStatus.NOT_YET_EXECUTED:
            command = CwlToolManager.build_command(workflow.template.path, workflow.workdir['inputs'])
            subprocess_event = threading.Event()
            thread = WorkflowThread(command, workflow, self, subprocess_event)  
            self.threads.append(thread)  
            thread.start()
            subprocess_event.wait()
            if thread.exception is not None:
                self.threads.remove(thread)
                raise thread.exception          
        else:
            raise AlreadyRunException(f"Workflow with GUID: '{workflow.GUID}' is already running or has been executed.")
        
        with self._run_lock:
            del self._guid_locks[GUID]
    

    def terminate(self, GUID: str):
        thread = self.get_thread(GUID)

        if thread is not None:
            os.kill(thread.process.pid, signal.SIGKILL)            
        else:
            raise NotRunningException(f'Workflow with GUID: {GUID} is not running or does not exist.')
    