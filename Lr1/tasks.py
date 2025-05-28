# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, auth, models
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return
@router.get("/", response_model=List[schemas.TaskOut])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return 

@router.get("/{task_id}", response_model=schemas.TaskOut)
def read_task(task_id: int, db: Session = Depends(get_db)):
    return

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_update: schemas.TaskCreate, db: Session = Depends(get_db)):
    return 

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return

# Эндпоинт для добавления записи учёта времени к задаче
@router.post("/{task_id}/time_entries", response_model=schemas.TimeEntryOut)
def add_time_entry(task_id: int, time_entry: schemas.TimeEntryCreate, db: Session = Depends(get_db)):
    return 

# Эндпоинт для добавления метки к задаче (many-to-many через ассоциативную сущность)
@router.post("/{task_id}/tags", response_model=schemas.TaskTagOut)
def add_tag(task_id: int, task_tag: schemas.TaskTagBase, db: Session = Depends(get_db)):
    return 
