# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, models
from auth import get_db

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User):
    return current_user

@router.get("/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Можно ограничить этот эндпоинт, если не хотите раскрывать список всех пользователей
    return crud.get_users(db, skip=skip, limit=limit)

@router.put("/me/password", response_model=schemas.UserOut)
def change_password(password_data: schemas.UserPasswordChange, db: Session = Depends(get_db), ):
    return
