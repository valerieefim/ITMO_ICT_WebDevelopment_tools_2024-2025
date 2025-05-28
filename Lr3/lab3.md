# Лабораторная работа: Интеграция парсера данных с FastAPI и использование очередей Celery в Docker

## Цель
Научиться упаковывать FastAPI приложения в Docker, создавать связь между основным приложением и сервисом парсинга данных, а также реализовать асинхронное выполнение задач с использованием очередей Celery и Redis.

## Архитектура проекта
Проект состоит из следующих компонентов:

- Основное FastAPI приложение (finance_app)

- Сервис парсера (parser_service)

- База данных PostgreSQL

- Redis для хранения очередей задач

- Celery для обработки асинхронных задач


## Подзадача 1: Упаковка сервисов в Docker

### Parser Service - Dockerfile
```dockerfile
FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r /app/req.txt

EXPOSE 8001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Finance App - Dockerfile
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r /app/req.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose для оркестрации сервисов
```yaml
services:
  db:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: database
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 2s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"

  main_service:
    build:
      context: ./Lr1/
    container_name: main_service
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    depends_on:
      - db
      - parser_service
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/database
      PARSER_URL: http://parser_service:8001
      SYNC_DB_URL: postgresql+psycopg2://postgres:postgres@db:5432/database

  parser_service:
    build:
      context: ./Lr3/
    container_name: parser_service
    command: uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ports:
      - "8001:8001"
    depends_on:
      - redis
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/database
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0


  celery_worker:
    build:
      context: ./Lr3/
    container_name: celery_worker
    command: celery -A celery_worker worker --loglevel=info
    depends_on:
      db:
        condition: service_healthy
      parser_service:
        condition: service_started
      redis:
        condition: service_started
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/database
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      PYTHONPATH: /app
    restart: on-failure

volumes:
  db_data:
```

## Подзадача 2: Реализация API парсера

### Parser Service - API
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery_worker import parse, celery_app
from task_2 import parser_async

app = FastAPI(title="Parser")

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse_pages(request: ParseRequest):
    try:
        await parser_async.main(request.url)
        return {"message": f"Pages are parsed from {request.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse/trigger")
async def trigger_parse(request: ParseRequest):
    task = parse.delay(request.url)
    return {"message": "Parsing started", "task_id": task.id}

@app.get("/parse/status/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "successful": result.successful() if result.ready() else None
    }
```

![Parse](parse.png)

## Подзадача 3: Настройка Celery для асинхронного выполнения задач

### Celery Worker (celery_worker.py)
```python
from celery import Celery
import asyncio
from task_2.parser_async import main
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "parser",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

@celery_app.task(name="parse_from_url")
def parse(url: str):
    asyncio.run(main(url))
```

![trigger](trigger.png)
![trigger_res](trigger_res.png)


## Подзадача 4: Интеграция парсера с основным приложением

### Router для вызова парсера из основного приложения
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/parse", tags=["Parser"])

PARSER_URL = os.getenv("PARSER_URL")

celery_app = Celery(
    "parser_celery",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)


class ParseRequest(BaseModel):
    url: str


@router.post("/")
async def call_parser(request: ParseRequest):
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(f"{PARSER_URL}/parse", json=request.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=response.text)


@router.post("/async-parse")
def enqueue_parse_task(request: ParseRequest):
    task = celery_app.send_task("parse_from_url", args=[request.url])
    return {"task_id": task.id, "status": task.status, "message": "Parsing started"}


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "successful": result.successful() if result.ready() else None,
    }
```

![async](async.png)
![async_res](async_res.png)

## Принцип работы системы

**Синхронный вызов парсера**:

   - Запрос приходит на эндпоинт `/parse` основного приложения

   - Основное приложение перенаправляет запрос в сервис парсера

   - Парсер выполняет обработку и возвращает результат

**Асинхронный вызов парсера через очередь**:

   - Запрос приходит на эндпоинт `/parse/async-parse` основного приложения

   - Основное приложение создает задачу в очереди Celery

   - Задача обрабатывается Celery worker'ом асинхронно

   - Клиент может проверить статус выполнения задачи по её ID

**Проверка статуса задачи**:

   - Запрос на эндпоинт `/parse/status/{task_id}` возвращает текущий статус задачи
   
   - При готовности результата, возвращается также и сам результат

## Схема взаимодействия компонентов

1. **finance_app** - основное приложение с бизнес-логикой
2. **parser_service** - микросервис для парсинга данных 
3. **redis** - хранилище для очередей задач
4. **celery_worker** - обработчик асинхронных задач
5. **db** - база данных PostgreSQL для хранения обработанных данных

Все компоненты взаимодействуют между собой в рамках Docker-сети, что обеспечивает изоляцию и независимость сервисов.