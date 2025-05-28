# app/main.py
from fastapi import FastAPI
from tasks import router as tasks_router
from auth import router as auth_router
from users import router as users_router
from parser import router as parse_router


app = FastAPI(title="Time Manager API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(parse_router, prefix="/parse", tags=["parse"])
