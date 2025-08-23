from exceptions.base import AppException


class InvalidCredentialError(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class EmailAlreadyRegisteredError(AppException):
    def __init__(self, message: str = "Email already registered"):
        super().__init__(message, status_code=400)


class InvalidRefreshTokenError(AppException):
    def __init__(self, message: str = "Invalid refresh token"):
        super().__init__(message, status_code=401)
