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