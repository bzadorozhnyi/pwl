from fastapi import FastAPI

from core.middlewares.log_requests import log_requests
from routes import auth

app = FastAPI()

app.include_router(auth.router)


app.middleware("http")(log_requests)
