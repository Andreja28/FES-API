from fastapi import HTTPException
from exceptions.api import YamlValidationException
class ValidationException(HTTPException):
    def __init__(self,exception: YamlValidationException):
        super().__init__(status_code=422, detail=None)
        self.detail = {
            "message": "Some files from inputs.yaml are missing.",
            "error": "Validation Error",
            "missing": exception.missing
        }