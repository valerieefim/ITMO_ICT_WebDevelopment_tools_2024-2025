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