from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqladmin import Admin

from admin.auth import get_admin_auth
from admin.user import UserAdmin
from core.db import engine
from core.middlewares.request_id import RequestIDMiddleware
from routes import auth, family_task, shopping_list, shopping_list_item, user, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin_auth = await get_admin_auth()
    admin = Admin(
        app,
        engine,
        authentication_backend=admin_auth,
        title="PWL Admin",
    )

    admin.add_view(UserAdmin)

    yield


app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")


app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(family_task.router, prefix="/api")
app.include_router(shopping_list.router, prefix="/api")
app.include_router(shopping_list_item.router, prefix="/api")
app.include_router(ws.router, prefix="/api")

app.add_middleware(RequestIDMiddleware)
