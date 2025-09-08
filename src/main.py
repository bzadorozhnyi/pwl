from fastapi import FastAPI

from core.middlewares.request_id import RequestIDMiddleware
from routes import auth, family_task, shopping_list, user, ws

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(family_task.router, prefix="/api")
app.include_router(shopping_list.router, prefix="/api")
app.include_router(ws.router, prefix="/api")

app.add_middleware(RequestIDMiddleware)
