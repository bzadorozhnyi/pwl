import uuid
from datetime import datetime
from email.message import EmailMessage

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from core.config import settings
from enums.mail_backend import MailBackend

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
)


class EmailService:
    async def send_email(
        self,
        subject: str,
        recipients: list[str],
        body: str,
        subtype: MessageType = MessageType.html,
    ):
        raise NotImplementedError("Subclasses must implement send_email")


class FastMailEmailService(EmailService):
    def __init__(self, fm: FastMail, sender: str):
        self.fm = fm
        self.sender = sender

    async def send_email(
        self,
        subject: str,
        recipients: list[str],
        body: str,
        subtype: MessageType = MessageType.html,
    ):
        msg = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=subtype,
        )
        await self.fm.send_message(msg)


class ConsoleEmailService(EmailService):
    def __init__(self, sender: str):
        self.sender = sender

    async def send_email(
        self,
        subject: str,
        recipients: list[str],
        body: str,
        subtype: MessageType = MessageType.html,
    ):
        line_separator = "\n" + "-" * 40 + "\n"
        for recipient in recipients:
            message = EmailMessage()
            message["Subject"] = f"{subject}"
            message["From"] = f"<{self.sender}>"
            message["To"] = f"<{recipient}>"
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
            message["Message-ID"] = f"<{uuid.uuid4().hex}>"
            message["Content-Type"] = f"text/{subtype.value}; charset=utf-8"

            print(line_separator)
            print(message.as_string())
            print(body)
            print(line_separator)


class InMemoryEmailService(EmailService):
    """Test double: stores sent messages for assertions."""

    def __init__(self, sender: str):
        self.sender = sender
        self.outbox: list[dict] = []

    async def send_email(
        self,
        subject: str,
        recipients: list[str],
        body: str,
        subtype: MessageType = MessageType.html,
    ):
        self.outbox.append(
            {
                "subject": subject,
                "recipients": recipients,
                "body": body,
                "subtype": subtype,
            }
        )


def get_fastmail() -> FastMail:
    return FastMail(conf)


def get_email_service_prod() -> EmailService:
    return FastMailEmailService(fm=get_fastmail(), sender=settings.MAIL_FROM)


def get_email_service_dev() -> EmailService:
    return ConsoleEmailService(settings.MAIL_FROM)


def get_email_service() -> EmailService:
    match settings.MAIL_BACKEND:
        case MailBackend.DEV:
            return get_email_service_dev()
        case MailBackend.PROD:
            return get_email_service_prod()
