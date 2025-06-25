from fastapi import APIRouter, Depends, Request
import os
from api.database.repositories.workflow import WorkflowRepository
from api.dto import FilesMetadataDTO
from data import utils
from data.entities.workflow import ExecutionStatus, WorkflowEntity
from fastapi.responses import FileResponse, JSONResponse

import exceptions.api.database as db_exceptions
import exceptions.api.fastapi as fastapi_exceptions
from validators import GuidValidator
import exceptions.manager as manager_exceptions
import exceptions.api as api_exceptions
from .routes_conf import (
    get_workflow_inputs_responses,
    get_workflow_log_responses,
    get_download_metadata_responses,
    get_workflow_results_responses,
    download_workflow_responses,
)

router = APIRouter()

# @router.get("/metadata")
# async def get_workflow_metadata(guid: str):
#     try:
#         workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
#         if workflow.metadata is None:
#             return JSONResponse(
#                 status_code=404,
#                 content={"message": f"Metadata for workflow with GUID: '{guid}' does not exist."}
#             )
#         return workflow.metadata
#     except db_exceptions.NotFoundException as e:
#         raise fastapi_exceptions.NotFoundException(exception=e)
#     except db_exceptions.DatabaseException as e:
#         raise fastapi_exceptions.InternalServerErrorException(exception=e)
    

@router.get("/inputs", responses=get_workflow_inputs_responses)
async def get_workflow_inputs(guid: str= Depends(GuidValidator.validate_query_param), file: str = None):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

    if file is None:
        return FileResponse(
            f"{workflow.workdir['inputs']}.zip", 
            media_type='application/octet-stream', 
            filename="inputs.zip"
        )
    else:
        filepath = os.path.join(workflow.workdir['inputs'], file)
        if not os.path.exists(filepath):
            return JSONResponse(
                status_code=404,
                content={"message": f"File '{file}' does not exist in the inputs directory of the workflow with GUID: '{guid}'."}
            )
        return FileResponse(
            filepath, 
            media_type='application/octet-stream', 
            filename=file
        )


@router.get("/log", responses=get_workflow_log_responses)
async def get_workflow_log(guid: str = Depends(GuidValidator.validate_query_param)):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
        if workflow.statis == ExecutionStatus.NOT_YET_EXECUTED:
            return JSONResponse(
                status_code=404,
                content={"message": f"Workflow with GUID: '{guid}' has not been executed yet."}
            )
        return FileResponse(
            os.path.join(workflow.workdir['logs'],"log.txt"), 
            media_type='application/octet-stream', 
            filename="log.txt"
        )
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)
    

@router.get("/metadata", responses=get_download_metadata_responses)
async def get_download_metadata(request: Request, guid: str= Depends(GuidValidator.validate_query_param)):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
        filesMetadataDTO = FilesMetadataDTO.from_entity(workflow)
        tree = utils.get_workflow_files_tree(workflow.workdir)
        filesMetadataDTO.add_tree(request.base_url, tree)
        return filesMetadataDTO
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

@router.get("/results", responses=get_workflow_results_responses)
async def get_workflow_results(guid: str= Depends(GuidValidator.validate_query_param), file: str = None):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))

        if workflow.status != ExecutionStatus.FINISHED_OK:
            return JSONResponse(
                status_code=409,
                content={"message": "Workflow is not finished successfully."}
            )

    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

    
    if file is None:
        return FileResponse(
            f"{workflow.workdir['results']}.zip", 
            media_type='application/octet-stream', 
            filename="rasults.zip"
        )
    else:
        filepath = os.path.join(workflow.workdir['results'], file)
        if not os.path.exists(filepath):
            return JSONResponse(
                status_code=404,
                content={"message": f"File '{file}' does not exist in the results directory of the workflow with GUID: '{guid}'."}
            )
        return FileResponse(
            filepath, 
            media_type='application/octet-stream', 
            filename=file
        )

@router.get("/", responses=download_workflow_responses)
async def download_workflow(guid: str = Depends(GuidValidator.validate_query_param)):
    try:
        workflow = WorkflowEntity(WorkflowRepository.get_workflow(guid))
        zip_path = utils.create_workflow_zip(workflow)

        return FileResponse(
            zip_path, 
            media_type='application/octet-stream', 
            filename="workflow.zip"
        )
        
    except db_exceptions.NotFoundException as e:
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)


