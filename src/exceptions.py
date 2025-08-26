from fastapi import HTTPException


class InputException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class AuthorizationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)
