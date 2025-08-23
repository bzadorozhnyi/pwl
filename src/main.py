from fastapi import FastAPI

from core.middlewares.exception_handler import ExceptionHandlerMiddleware
from core.middlewares.request_id import RequestIDMiddleware
from routes import auth

app = FastAPI()

app.include_router(auth.router)


app.add_middleware(RequestIDMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)
