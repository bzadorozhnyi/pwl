from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqladmin import Admin

from admin.auth import get_admin_auth
from admin.family import FamilyAdmin, FamilyMemberAdmin
from admin.family_task import FamilyTaskAdmin
from admin.shopping_list import ShoppingListAdmin
from admin.shopping_list_item import ShoppingListItemAdmin
from admin.user import UserAdmin
from admin.verify_token import VerifyTokenAdmin
from core.db import engine
from core.middlewares.request_id import RequestIDMiddleware
from routes import (
    auth,
    family_task,
    recipes,
    shopping_list,
    shopping_list_item,
    user,
    ws,
)


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
    admin.add_view(FamilyAdmin)
    admin.add_view(FamilyMemberAdmin)
    admin.add_view(FamilyTaskAdmin)
    admin.add_view(ShoppingListAdmin)
    admin.add_view(ShoppingListItemAdmin)
    admin.add_view(VerifyTokenAdmin)

    yield


app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")


app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(family_task.router, prefix="/api")
app.include_router(shopping_list.router, prefix="/api")
app.include_router(shopping_list_item.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(ws.router, prefix="/api")

app.add_middleware(RequestIDMiddleware)
