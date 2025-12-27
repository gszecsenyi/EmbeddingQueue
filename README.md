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

### 3. Submit a text for embedding

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/tasks" `
  -Method POST `
  -Headers @{ "Authorization" = "Bearer your-secret-token" } `
  -ContentType "application/json" `
  -Body '{"text": "The quick brown fox jumps over the lazy dog"}'
```

**Bash/curl:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog"}'
```

Response:
```json
{"id": "550e8400-e29b-41d4-a716-446655440000"}
```

### 4. Check the result

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000" `
  -Headers @{ "Authorization" = "Bearer your-secret-token" }
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "The quick brown fox jumps over the lazy dog",
  "status": "completed",
  "embedding": [0.123, -0.456, 0.789, ...],
  "error": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05"
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks` | Submit text for embedding |
| `GET` | `/tasks/{id}` | Get task status and result |
| `GET` | `/tasks/{id}/result` | Get only the embedding |
| `GET` | `/health` | Health check |

All endpoints require `Authorization: Bearer your-secret-token` header.

## Configuration

Edit `docker-compose.yml` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_TOKEN` | `your-secret-token` | API authentication token |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama model to use |
| `POLL_INTERVAL` | `2` | Worker poll frequency (seconds) |

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
└── data/             # SQLite database (persistent)
```

## Task States

- `pending` - Waiting to be processed
- `processing` - Worker is generating embedding
- `completed` - Embedding ready
- `failed` - Error occurred (check `error` field)
