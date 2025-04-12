# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, models
from auth import get_db, get_current_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Можно ограничить этот эндпоинт, если не хотите раскрывать список всех пользователей
    return crud.get_users(db, skip=skip, limit=limit)

@router.put("/me/password", response_model=schemas.UserOut)
def change_password(password_data: schemas.UserPasswordChange, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Проверка старого пароля
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")
    return crud.update_user_password(db, current_user, password_data.new_password)
