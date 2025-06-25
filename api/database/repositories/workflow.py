import api.database.models as models
from api.database import SessionLocal
from data import utils
from exceptions.api.database import DatabaseException, NotFoundException, RunningException
import xml.etree.ElementTree as ET

class WorkflowRepository:

    @classmethod
    def get_workflows(cls, template=None, status=None, userID=None):
        session = SessionLocal()
        try:
            workflows = session.query(models.Workflow
                ).filter((models.Workflow.template_name == template) if template else True
                ).filter((models.Workflow.status == status.value) if status else True).all()
            
            
            if userID is not None:
                workflows = [workflow for workflow in workflows if workflow.meta is not None and ET.fromstring(workflow.meta).find('userID').text == userID]
            return workflows
        except Exception as e:
            # Handle session creation error (e.g., database connection issue)
            raise DatabaseException(f"Error trying to get workflows. Database connection error: '{str(e)}'")
        finally:
            session.close()

    @classmethod
    def get_workflow(cls, GUID: str):
        session = SessionLocal()
        try:
            workflow = session.query(models.Workflow).filter(models.Workflow.GUID == GUID).join(models.Template).first()
            if workflow:
                return workflow  # Assuming 'description' is a field in your Workflow model
            else:
                raise NotFoundException(f"Error trying to get workflow with GUID '{GUID}'. Workflow with GUID '{GUID}' does not exist!")
        except NotFoundException as e:
            # Handle not found error specifically
            raise e
        except Exception as e:
            # Handle session creation error (e.g., database connection issue)
            raise DatabaseException(f"Error trying to get workflow with GUID '{GUID}'. ErrorDatabase connection error: '{str(e)}'")
        finally:
            session.close()

    @classmethod
    def create_workflow(cls, GUID: str, template: str, metadata: str = None):
        session = SessionLocal()
        try:
            workflow = models.Workflow(GUID=GUID, template_name=template, metadata=metadata)
            
            session.add(workflow)
            session.commit()
            return workflow
        except Exception as e:
            raise DatabaseException(f"Error trying to create a workflow with GUID: '{GUID}'. Database connection error: '{str(e)}'")
        finally:
            session.close()

    @classmethod
    def update_status(cls, GUID: str, status: str, PID: int = None):
        session = SessionLocal()
        try:
            db_workflow = session.query(models.Workflow).filter(models.Workflow.GUID == GUID).first()
            if db_workflow:
                db_workflow.status = status.value
                db_workflow.PID = PID if PID is not None else db_workflow.PID
                session.commit()
                return
            else:
                raise NotFoundException(f"Error trying to get workflow with GUID '{GUID}'. Workflow with GUID '{GUID}' does not exist!")
        except NotFoundException as e:  
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise DatabaseException(f"Error trying to update status for workflow with GUID: '{GUID}'. Database connection error: '{str(e)}'")
        finally:
            session.close()  

    @classmethod
    def delete_workflow(cls, GUID: str):
        session = SessionLocal()
        try:
            workflow = session.query(models.Workflow).filter(models.Workflow.GUID == GUID).first()
            if workflow.status == "RUNNING":
                raise RunningException(f"Error trying to delete workflow with GUID '{GUID}'. Workflow with GUID '{GUID}' is currently running!")
            if workflow:
                utils.delete_workdir(GUID)
                session.delete(workflow)
                session.commit()
                return 
            else:
                raise NotFoundException(f"Error trying to delete workflow with GUID '{GUID}'. Workflow with GUID '{GUID}' does not exist!")
        except NotFoundException as e:
            session.rollback()
            raise e
        except RunningException as e:
            session.rollback()
            raise e
        except Exception as e:
            session.rollback()
            raise DatabaseException(f"Error trying to delete workflow with GUID: '{GUID}'. Database connection error: '{str(e)}'")
        finally:
            session.close()