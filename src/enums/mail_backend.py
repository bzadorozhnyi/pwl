from enum import StrEnum


class MailBackend(StrEnum):
    FASTAPI_MAIL = "fastapi_mail"
    CONSOLE = "console"
    IN_MEMORY = "in_memory"
