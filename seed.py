#!/usr/bin/env python
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from passlib.context import CryptContext

# Инициализируем контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_users(session: Session):
    users_data = [
        {"username": "alice", "email": "alice@example.com", "password": "password"},
        {"username": "bob", "email": "bob@example.com", "password": "password"},
        {"username": "charlie", "email": "charlie@example.com", "password": "password"},
    ]
    users = []
    for user_data in users_data:
        hashed = pwd_context.hash(user_data["password"])
        user = models.User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        users.append(user)
        print(f"Создан пользователь: {user.username}")
    return users

def seed_tags(session: Session):
    tag_names = ["urgent", "work", "personal", "home", "exercise"]
    tags = []
    for name in tag_names:
        tag = models.Tag(name=name)
        session.add(tag)
        session.commit()
        session.refresh(tag)
        tags.append(tag)
        print(f"Создана метка: {tag.name}")
    return tags

def seed_tasks(session: Session, users):
    tasks = []
    for user in users:
        # Для каждого пользователя создаём 3 задачи
        for i in range(3):
            task = models.Task(
                title=f"Task {i+1} для {user.username}",
                description=f"Описание задачи {i+1} для пользователя {user.username}",
                deadline=datetime.utcnow() + timedelta(days=random.randint(1, 10)),
                priority=random.randint(1, 5),
                user_id=user.id
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            tasks.append(task)
            print(f"Создана задача: {task.title} для пользователя {user.username}")
    return tasks

def seed_time_entries(session: Session, tasks):
    for task in tasks:
        # Для каждой задачи создаём от 1 до 3 записей учёта времени
        num_entries = random.randint(1, 3)
        for _ in range(num_entries):
            duration = random.randint(15, 120)
            time_entry = models.TimeEntry(
                task_id=task.id,
                duration=duration,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            )
            session.add(time_entry)
        session.commit()
        print(f"Добавлено {num_entries} записей учёта времени для задачи {task.title}")

def seed_task_tags(session: Session, tasks, tags):
    # Для каждой задачи случайным образом выбираем от 1 до 3 меток
    for task in tasks:
        num_tags = random.randint(1, 3)
        chosen_tags = random.sample(tags, num_tags)
        for tag in chosen_tags:
            note = f"Комментарий для метки {tag.name} задачи {task.title}"
            task_tag = models.TaskTag(
                task_id=task.id,
                tag_id=tag.id,
                note=note
            )
            session.add(task_tag)
        session.commit()
        print(f"Назначено {num_tags} меток для задачи {task.title}")

def main():
    session = SessionLocal()
    try:
        print("Начало наполнения базы данных синтетическими данными...")
        users = seed_users(session)
        tags = seed_tags(session)
        tasks = seed_tasks(session, users)
        seed_time_entries(session, tasks)
        seed_task_tags(session, tasks, tags)
        print("Наполнение базы данных завершено.")
    except Exception as e:
        session.rollback()
        print("Ошибка:", e)
    finally:
        session.close()

if __name__ == "__main__":
    main()
