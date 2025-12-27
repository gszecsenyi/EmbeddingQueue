# Embedding Queue

A simple distributed system for offloading text embedding tasks to a local GPU.

## What is this?

If you have a machine with a GPU but want to run your main application somewhere else (like AWS), this project lets you:

1. **Submit texts** from anywhere via a simple REST API
2. **Process embeddings** on your local GPU using Ollama
3. **Retrieve results** when they're ready

The queue server runs in the cloud, your GPU worker runs locally, and they communicate over HTTP.

## Architecture

```
Your App (cloud)          Queue Server (cloud)           Your PC (local GPU)
      │                          │                              │
      ├── Submit text ──────────►│                              │
      │                          │◄──── Worker polls for tasks ─┤
      │                          │                              │
      │                          │──── Send text to process ───►│
      │                          │                              ├── Ollama generates
      │                          │◄──── Return embedding ───────┤    embedding
      │                          │                              │
      ◄── Get result ────────────┤                              │
```

## Quick Start

### 1. Start the services

```bash
docker-compose up --build
```

### 2. Download an embedding model (first time only)

```bash
docker exec -it embeddingqueue-ollama-1 ollama pull nomic-embed-text
```

### 3. Get embeddings (OpenAI-compatible)

**curl:**
```bash
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"input": "The quick brown fox jumps over the lazy dog", "model": "nomic-embed-text"}'
```

**Python (OpenAI SDK):**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-secret-token",
    base_url="http://localhost:8000/v1"
)

response = client.embeddings.create(
    input="The quick brown fox jumps over the lazy dog",
    model="nomic-embed-text"
)

embedding = response.data[0].embedding
```

**Response (OpenAI format):**
```json
{
  "object": "list",
  "data": [{"object": "embedding", "embedding": [0.123, -0.456, ...], "index": 0}],
  "model": "nomic-embed-text"
}
```

The server waits for the result (default 10 seconds, max 30 seconds). If processing takes longer, it returns a task ID:

```json
{"id": "550e8400-e29b-41d4-a716-446655440000"}
```

Then poll for the result:

```bash
curl http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer your-secret-token"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/embeddings` | **OpenAI-compatible** - sync with long polling |
| `GET` | `/tasks/{id}` | Get task status and result (for polling) |
| `GET` | `/tasks/{id}/result` | Get only the embedding |
| `GET` | `/health` | Health check |

All endpoints require `Authorization: Bearer your-secret-token` header.

### OpenAI Endpoint Details

`POST /v1/embeddings`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input` | string | required | Text to embed |
| `model` | string | `nomic-embed-text` | Model name (optional) |
| `wait_seconds` | int | `10` | Wait time in seconds (0 = return ID immediately, max 30) |

## Configuration

Edit `.env` file to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_TOKEN` | `your-secret-token` | API authentication token |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama model to use |
| `POLL_INTERVAL` | `2` | Worker poll frequency (seconds) |
| `SERVER_PORT` | `8000` | Server port |
| `DB_PATH` | `data/embedding_queue.db` | SQLite database path |

## Requirements

- Docker & Docker Compose
- NVIDIA GPU with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## Project Structure

```
EmbeddingQueue/
├── server/           # FastAPI queue server
│   ├── main.py       # API endpoints
│   ├── database.py   # SQLite operations
│   ├── models.py     # Request/response models
│   └── config.py     # Configuration
├── worker/           # GPU worker client
│   ├── worker.py     # Polling loop
│   ├── embedder.py   # Ollama client
│   └── config.py     # Configuration
├── docker-compose.yml
├── .env              # Environment variables
└── data/             # SQLite database (persistent)
```

## Task States

- `pending` - Waiting to be processed
- `processing` - Worker is generating embedding
- `completed` - Embedding ready
- `failed` - Error occurred (check `error` field)
