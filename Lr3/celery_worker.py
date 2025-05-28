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
