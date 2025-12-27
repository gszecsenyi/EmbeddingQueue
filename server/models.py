from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    text: str
    wait_seconds: Optional[int] = None


class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int = 0


class OpenAIEmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str


class AsyncTaskResponse(BaseModel):
    id: str
    status: str = "processing"
    message: str = "Task queued for async processing"


# OpenAI-compatible request model
class OpenAIEmbeddingRequest(BaseModel):
    input: str  # text to embed
    model: Optional[str] = None  # optional, uses server default
    wait_seconds: Optional[int] = 10  # extension: async support (default 10s)


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
