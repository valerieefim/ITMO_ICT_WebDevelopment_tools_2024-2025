# app/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функции для работы с пользователями
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.User, new_password: str) -> models.User:
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


# Функции для работы с задачами
def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    db_task = models.Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).filter(models.Task.user_id == user_id).offset(skip).limit(limit).all()

def update_task(db: Session, task_id: int, task_update: schemas.TaskCreate) -> Optional[models.Task]:
    task = get_task(db, task_id)
    if task:
        for key, value in task_update.dict().items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
    return task

def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

# Функции для работы с учётом времени
def create_time_entry(db: Session, task_id: int, time_entry: schemas.TimeEntryCreate) -> models.TimeEntry:
    db_time_entry = models.TimeEntry(**time_entry.dict(), task_id=task_id)
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

# Функции для работы с метками и ассоциацией TaskTag
def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def add_tag_to_task(db: Session, task_id: int, task_tag: schemas.TaskTagBase) -> models.TaskTag:
    db_task_tag = models.TaskTag(task_id=task_id, tag_id=task_tag.tag_id, note=task_tag.note)
    db.add(db_task_tag)
    db.commit()
    db.refresh(db_task_tag)
    return db_task_tag
