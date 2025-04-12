# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, auth, models
from auth import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_task(db, task, user_id=current_user.id)

@router.get("/", response_model=List[schemas.TaskOut])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=schemas.TaskOut)
def read_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, task_update: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.update_task(db, task_id, task_update)

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if crud.delete_task(db, task_id):
        return {"detail": "Задача удалена"}
    raise HTTPException(status_code=400, detail="Ошибка удаления")

# Эндпоинт для добавления записи учёта времени к задаче
@router.post("/{task_id}/time_entries", response_model=schemas.TimeEntryOut)
def add_time_entry(task_id: int, time_entry: schemas.TimeEntryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.create_time_entry(db, task_id, time_entry)

# Эндпоинт для добавления метки к задаче (many-to-many через ассоциативную сущность)
@router.post("/{task_id}/tags", response_model=schemas.TaskTagOut)
def add_tag(task_id: int, task_tag: schemas.TaskTagBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = crud.get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return crud.add_tag_to_task(db, task_id, task_tag)
