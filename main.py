# app/main.py
from fastapi import FastAPI
from database import engine, Base
from routers import auth as auth_router, tasks as tasks_router, users as users_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Time Manager API")

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router.router, prefix="/tasks", tags=["tasks"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
