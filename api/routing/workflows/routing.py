from fastapi import APIRouter, Depends, UploadFile, Form, File, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from data.entities import WorkflowEntity, TemplateEntity
from api.database.repositories import *
from api.dto import WorkflowDTO
from data.entities.workflow import ExecutionStatus
from manager import WorkflowManager

import exceptions.api.database as db_exceptions
import exceptions.api.fastapi as fastapi_exceptions
import exceptions.manager as manager_exceptions
import exceptions.api as api_exceptions
from validators import GuidValidator
from .routes_conf import (
    create_workflow_responses,
    list_workflows_responses,
    get_workflow_info_responses,
    run_workflow_responses,
    stop_workflow_responses,
    delete_workflow_responses,
)

router = APIRouter()

@router.post(
        "/create",
        response_model=WorkflowDTO,
        responses=create_workflow_responses
)
async def create_workflow(
    yaml: UploadFile = File(...),
    inputs: List[UploadFile] = File([]),
    template: str = Form(...)
):
    try:
        template_entity = TemplateEntity(template=TemplateRepository.get_template(template))
        workflow = WorkflowEntity(template=template_entity, yaml=yaml, inputs=inputs)
        return WorkflowDTO.from_entity(workflow)
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)
    except api_exceptions.YamlValidationException as e:
        raise fastapi_exceptions.ValidationException(exception=e)

@router.get(
    "/",
    responses=list_workflows_responses
)
async def list_workflows(
    template: Optional[str] = None,
    status: Optional[ExecutionStatus] = None,
    userID: Optional[str] = None
):
    workflows = WorkflowRepository.get_workflows(template=template, status=status, userID=userID)
    return [WorkflowDTO.from_entity(WorkflowEntity(workflow)) for workflow in workflows]

@router.get(
    "/info",
    responses=get_workflow_info_responses
)
async def get_workflow_info(guid: str = Depends(GuidValidator.validate_query_param)):
    try:
        workflow = WorkflowManager.get_workflow(guid)
        if workflow is None:
            workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
        return WorkflowDTO.from_entity(workflow)
    except db_exceptions.NotFoundException as e:
        # Handle session creation error (e.g., database connection issue)
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        # Handle not found error specifically
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

# @router.get("/status")
# async def get_workflow_status(guid: str):
#     workflow = WorkflowManager.get_workflow(guid)
#     if workflow is None:
#         workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
#     return WorkflowDTO.from_entity(workflow)

@router.post(
    "/run",
    responses=run_workflow_responses
)
async def run_workflow(
    GUID: str = Depends(GuidValidator.validate_form_param)
):
    try:
        WorkflowManager.run(GUID)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Workflow with GUID: {GUID} has been started successfully."}
        )
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except manager_exceptions.RunningException as e:
        raise fastapi_exceptions.LockedException(exception=e)
    except manager_exceptions.AlreadyRunException as e:
        raise fastapi_exceptions.ConflictException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

@router.post(
    "/stop",
    responses=stop_workflow_responses
)
async def stop_workflow(
    GUID: str = Depends(GuidValidator.validate_form_param)
):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(GUID))
        WorkflowManager.terminate(GUID)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Workflow with GUID: {GUID} has been terminated successfully."}
        )
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except manager_exceptions.NotRunningException as e:
        raise fastapi_exceptions.ConflictException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

@router.delete(
    "/",
    responses=delete_workflow_responses
)
async def delete_workflow(
    GUID: str  = Depends(GuidValidator.validate_form_param)
):
    try:
        WorkflowRepository.delete_workflow(GUID)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Workflow with GUID: {GUID} has been  successfully."}
        )
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.RunningException as e:
        raise fastapi_exceptions.LockedException(exception=e)
    except manager_exceptions.AlreadyRunException as e:
        raise fastapi_exceptions.ConflictException(exception=e)

