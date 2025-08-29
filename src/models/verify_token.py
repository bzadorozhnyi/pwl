import uuid
from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from core.config import settings


class VerifyToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    email: EmailStr = Field(index=True, nullable=False)
    token: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(
            hours=settings.VERIFY_TOKEN_EXPIRE_HOURS
        )

    @property
    def restore_link(self):
        base_domain = settings.BASE_UI_DOMAIN
        protocol = settings.UI_URL_PROTOCOL

        return f"{protocol}{base_domain}/password/reset/{self.token}"
