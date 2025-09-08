from fastapi import FastAPI
from sqladmin import Admin

from admin.auth import AdminAuth
from admin.user import UserAdmin
from core.db import engine
from core.middlewares.request_id import RequestIDMiddleware
from routes import auth, family_task, shopping_list, shopping_list_item, user, ws

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(family_task.router, prefix="/api")
app.include_router(shopping_list.router, prefix="/api")
app.include_router(shopping_list_item.router, prefix="/api")
app.include_router(ws.router, prefix="/api")

app.add_middleware(RequestIDMiddleware)

authentication_backend = AdminAuth(secret_key="super-secret")  # secret_key for session
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
