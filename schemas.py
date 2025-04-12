# app/schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Схемы для пользователей
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str

# Схемы для меток
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int

    class Config:
        orm_mode = True

# Ассоциативная схема для TaskTag
class TaskTagBase(BaseModel):
    tag_id: int
    note: Optional[str] = None

class TaskTagOut(BaseModel):
    tag: TagOut
    note: Optional[str] = None

    class Config:
        orm_mode = True

# Схемы для задач
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    owner: UserOut
    time_entries: List["TimeEntryOut"] = []
    tags: List[TaskTagOut] = []

    class Config:
        orm_mode = True

# Схемы для учёта времени
class TimeEntryBase(BaseModel):
    duration: int

class TimeEntryCreate(TimeEntryBase):
    pass

class TimeEntryOut(TimeEntryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Для вложенности взаимных ссылок
TaskOut.update_forward_refs()
