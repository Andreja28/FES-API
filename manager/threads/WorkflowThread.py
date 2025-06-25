import threading
import subprocess
import os, signal
from api.database.repositories import WorkflowRepository
from data.entities.workflow import ExecutionStatus
from manager.WorkflowManager import IWorkflowManager
from exceptions.manager import SubprocessException
import data.utils as utils

class WorkflowThread(threading.Thread):
    exception = None
    def __init__(self, command, workflow, wfm: IWorkflowManager, event:threading.Event):
        super().__init__()
        self.workflow = workflow
        self.command = command
        self.cwd = os.path.abspath(workflow.workdir['results'])
        self.log_file = os.path.abspath(f"{workflow.workdir['logs']}/log.txt")
        self.wfm = wfm
        self.event = event if event is not None else None

    def run(self):
        try:
            process = subprocess.Popen(
                                self.command, 
                                shell=True, 
                                cwd=self.cwd, 
                                stdout=open(self.log_file, 'w'), 
                                stderr=open(self.log_file, 'w')
                            )
        except Exception as e:
            self.event.set()
            self.exception = SubprocessException(f"Failed to start subprocess with command '{self.command}'. Log file: {self.log_file}. General Error: {str(e)}")
        
        self.event.set()
        self.process = process
        self.workflow.status = ExecutionStatus.RUNNING
        self.workflow.PID = process.pid
        WorkflowRepository.update_status(self.workflow.GUID, self.workflow.status, self.workflow.PID)
        process.wait()
        self.wfm.threads.remove(self)
        
        self.workflow.status = ExecutionStatus.FINISHED_OK 
        if process.returncode == signal.SIGKILL:
            self.workflow.status = ExecutionStatus.TERMINATED
        elif process.returncode != 0:
            self.workflow.status = ExecutionStatus.FINISHED_ERROR
        self.workflow.PID = None
        
        if self.workflow.status == ExecutionStatus.FINISHED_OK:
            utils.zip_folder(self.workflow.workdir['results'], self.workflow.workdir['results'])
        WorkflowRepository.update_status(self.workflow.GUID, self.workflow.status, self.workflow.PID)
        
        