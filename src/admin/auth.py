from fastapi import Request
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if email == "another_user@email.com" and password == "password12345":
            request.session.update({"token": "authenticated"})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()

        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session
