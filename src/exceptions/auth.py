from exceptions.base import AppException


class InvalidCredentialException(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)


class EmailAlreadyRegisteredException(AppException):
    def __init__(self, message: str = "Email already registered"):
        super().__init__(message, status_code=400)


class InvalidRefreshTokenException(AppException):
    def __init__(self, message: str = "Invalid refresh token"):
        super().__init__(message, status_code=401)
