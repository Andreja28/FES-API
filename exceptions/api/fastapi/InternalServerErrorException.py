from fastapi import HTTPException

class InternalServerErrorException(HTTPException):
    def __init__(self,exception: Exception):
        super().__init__(status_code=500, detail=exception.message)