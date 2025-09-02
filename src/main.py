from fastapi import FastAPI

from core.middlewares.request_id import RequestIDMiddleware
from routes import auth, user

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")


app.add_middleware(RequestIDMiddleware)
