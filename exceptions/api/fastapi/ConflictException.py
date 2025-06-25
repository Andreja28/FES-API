from fastapi import HTTPException

class ConflictException(HTTPException):
    def __init__(self,exception: Exception):
        super().__init__(status_code=409, detail=str(exception))