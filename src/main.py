from fastapi import FastAPI

from core.middlewares.request_id import RequestIDMiddleware
from routes import auth

app = FastAPI()

app.include_router(auth.router, prefix="/api")


app.add_middleware(RequestIDMiddleware)
