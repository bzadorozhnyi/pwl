from exceptions.base import AppException


class AuthException(AppException):
    @classmethod
    def invalid_credential(cls, message: str = "Invalid credentials") -> AppException:
        return cls(message, status_code=401)

    @classmethod
    def email_already_registered(
        cls, message: str = "Email already registered"
    ) -> AppException:
        return cls(message, status_code=400)

    @classmethod
    def invalid_refresh_token(
        cls, message: str = "Invalid refresh token"
    ) -> AppException:
        return cls(message, status_code=401)
