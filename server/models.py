from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    text: str


class TaskResponse(BaseModel):
    id: str
    text: str
    status: str
    embedding: Optional[list[float]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


class TaskResult(BaseModel):
    id: str
    embedding: list[float]


class WorkerCompleteRequest(BaseModel):
    embedding: list[float]


class WorkerFailRequest(BaseModel):
    error: str
