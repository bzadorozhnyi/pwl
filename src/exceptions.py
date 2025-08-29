from collections.abc import Mapping

from fastapi import HTTPException


class InputException(HTTPException):
    def __init__(self, detail: str, headers: Mapping[str, str] | None = None):
        super().__init__(status_code=400, detail=detail, headers=headers)


class AuthorizationException(HTTPException):
    def __init__(self, detail: str, headers: Mapping[str, str] | None = None):
        super().__init__(status_code=401, detail=detail, headers=headers)


class NotFoundException(HTTPException):
    def __init__(self, detail: str, headers: Mapping[str, str] | None = None):
        super().__init__(status_code=404, detail=detail, headers=headers)


class GoneException(HTTPException):
    def __init__(self, detail: str, headers: Mapping[str, str] | None = None):
        super().__init__(status_code=410, detail=detail, headers=headers)
