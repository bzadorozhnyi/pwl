import uuid
from typing import Annotated

from fastapi import BackgroundTasks, Depends
from fastapi_mail import MessageType

from core.jwt import AuthJWTService, get_auth_jwt_service
from core.logging import logger
from exceptions import GoneException, NotFoundException
from models.verify_token import VerifyToken
from repositories.user import UserRepository, get_user_repository
from repositories.verify_token import VerifyTokenRepository, get_verify_token_repository
from services.email import EmailService, get_email_service


class PasswordResetService:
    def __init__(
        self,
        user_repository: UserRepository,
        verify_token_repository: VerifyTokenRepository,
        auth_jwt_service: AuthJWTService,
        email_service: EmailService,
        background_tasks: BackgroundTasks,
    ):
        self.user_repository = user_repository
        self.verify_token_repository = verify_token_repository
        self.auth_jwt_service = auth_jwt_service
        self.email_service = email_service
        self.background_tasks = background_tasks

    async def request_forgot_password(self, email: str):
        user = await self.user_repository.get_by_identifier(email, allow_username=False)

        if user is None:
            return

        verify_token = await self.verify_token_repository.get_by_email(email)
        if verify_token is None:
            verify_token = VerifyToken(user_id=user.id, email=email)
            await self.verify_token_repository.create(verify_token)
        else:
            verify_token.token = uuid.uuid4()
            await self.verify_token_repository.update(verify_token)

        await self._send_email_to_restore_password(verify_token)

        logger.info(f"Password reset email sent to user with id={verify_token.user_id}")

    async def update_forgotten_password(self, token: uuid.UUID, new_password: str):
        verify_token = await self.verify_token_repository.get_by_token(token)
        if verify_token is None:
            raise NotFoundException("The link is not found")

        if verify_token.is_expired():
            raise GoneException("Password reset link has expired")

        user = await self.user_repository.get_by_identifier(
            verify_token.email, allow_username=False
        )

        new_password_hash = self.auth_jwt_service.get_password_hash(new_password)
        user.password = new_password_hash
        await self.user_repository.update(user)

        await self.verify_token_repository.delete(verify_token.id)

        logger.info(f"Successfully updated password for user with id={user.id}")

    async def _send_email_to_restore_password(self, verify_token: VerifyToken):
        subject = "PWL Restore Password"
        plain_text = f"Restore password link: {verify_token.restore_link}"

        self.background_tasks.add_task(
            self.email_service.send_email,
            subject=subject,
            recipients=[verify_token.email],
            body=plain_text,
            subtype=MessageType.plain,
        )


def get_password_reset_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    verify_token_repository: Annotated[
        VerifyTokenRepository, Depends(get_verify_token_repository)
    ],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    background_tasks: BackgroundTasks,
) -> PasswordResetService:
    return PasswordResetService(
        user_repository=user_repository,
        verify_token_repository=verify_token_repository,
        auth_jwt_service=auth_jwt_service,
        email_service=email_service,
        background_tasks=background_tasks,
    )
