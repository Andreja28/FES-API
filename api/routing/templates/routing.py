from fastapi import APIRouter
from api.database.repositories import TemplateRepository
from fastapi import Form
from api.dto import TemplateDTO
from data.entities import TemplateEntity
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.openapi.models import Response as OpenAPIResponse
from typing import List
import exceptions.api.database as db_exceptions
import exceptions.api.fastapi as fastapi_exceptions

from .routes_conf import (
    get_templates_responses,
    get_template_responses,
    set_template_description_responses,
    delete_template_description_responses,
)

router = APIRouter()

@router.get(
    "/",
    response_model=List[TemplateDTO],
    responses=get_templates_responses
)
async def get_templates():
    try:
        template_objects = TemplateRepository.get_templates()
        templates = TemplateEntity.get_templates(template_objects)
        return [TemplateDTO.from_model(template) for template in templates]
    except db_exceptions.DatabaseException as e:
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

@router.get(
    "/{template}",
    response_model=TemplateDTO,
    responses=get_template_responses
)
async def get_template(template: str):
    try:
        template = TemplateRepository.get_template(template)
        return template
    except db_exceptions.NotFoundException as e:
        # Handle session creation error (e.g., database connection issue)
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        # Handle not found error specifically
        raise fastapi_exceptions.InternalServerErrorException(exception=e)

@router.post(
    "/description",
    responses=set_template_description_responses
)
async def set_template_description(
    template: str = Form(...), description: str = Form(...)
):
    try:
        TemplateRepository.set_template_description(template, description)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Template description set successfully."}
        )
    except db_exceptions.NotFoundException as e:
        # Handle session creation error (e.g., database connection issue)
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        # Handle not found error specifically
        raise fastapi_exceptions.InternalServerErrorException(exception=e)
    

@router.delete(
    "/description",
    responses=delete_template_description_responses
)
async def delete_template_description(template: str):
    try:
        TemplateRepository.delete_template_description(template)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Template description deleted successfully."}
        )
    except db_exceptions.NotFoundException as e:
        # Handle session creation error (e.g., database connection issue)
        raise fastapi_exceptions.NotFoundException(exception=e)
    except db_exceptions.DatabaseException as e:
        # Handle not found error specifically
        raise fastapi_exceptions.InternalServerErrorException(exception=e)