from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from core.db import AsyncSessionProxy, async_session
from core.jwt import get_auth_jwt_service
from repositories.family import get_family_repository
from repositories.shopping_list import get_shopping_list_repository
from repositories.user import get_user_repository
from schemas.user import UserAuthCredentialsIn
from services.user import UserService, get_user_service


class AdminAuth(AuthenticationBackend):
    def __init__(self, *, user_service: UserService, secret_key: str):
        self.user_service = user_service
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        user_credentials = UserAuthCredentialsIn(identifier=email, password=password)
        user_with_tokens = await self.user_service.login_admin(
            user_credentials=user_credentials
        )

        if user_with_tokens:
            request.session.update({"token": user_with_tokens.tokens.access_token})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()

        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if token:
            try:
                user = await self.user_service.get_user_from_token(token)
                if user and user.is_admin:
                    return True
            except Exception:
                request.session.clear()

        return False


async def get_admin_auth() -> AdminAuth:
    async with async_session() as session:
        proxy_session = AsyncSessionProxy(session)

        user_repo = get_user_repository(proxy_session)
        family_repo = get_family_repository(proxy_session)
        shopping_list_repo = get_shopping_list_repository(proxy_session)
        auth_jwt_service = get_auth_jwt_service()

        user_service = get_user_service(
            session=proxy_session,
            user_repository=user_repo,
            family_repository=family_repo,
            shopping_list_repository=shopping_list_repo,
            auth_jwt_service=auth_jwt_service,
        )

        return AdminAuth(user_service=user_service, secret_key="your-secret-key")
