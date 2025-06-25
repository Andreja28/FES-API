from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self,exception: Exception):
        super().__init__(status_code=404, detail=str(exception))