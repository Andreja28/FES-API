from fastapi import HTTPException, Form
from data import utils

class GuidValidator:
    @staticmethod
    def validate_query_param(guid: str) -> str:
        if utils.validate_GUID(guid):
            return guid
        raise HTTPException(status_code=422, detail="Invalid GUID format")
    
    @staticmethod
    def validate_form_param(guid: str = Form(...)) -> str:
        if utils.validate_GUID(guid):
            return guid
        raise HTTPException(status_code=422, detail="Invalid GUID format")
    