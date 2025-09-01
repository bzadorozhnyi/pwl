from fastapi import FastAPI

from core.middlewares.request_id import RequestIDMiddleware
from routes import auth, family_task, user

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(family_task.router, prefix="/api")


app.add_middleware(RequestIDMiddleware)
