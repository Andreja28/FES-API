from fastapi import HTTPException

class LockedException(HTTPException):
    def __init__(self,exception: Exception):
        super().__init__(status_code=423, detail=str(exception))