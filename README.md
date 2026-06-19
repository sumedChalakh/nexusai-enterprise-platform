# NexusAI — Multi-Agent RAG Enterprise Knowledge Platform

NexusAI is a full-stack platform that lets users upload documents and ask questions against them using retrieval-augmented generation (RAG). It combines a FastAPI backend, a Next.js 15 frontend, PostgreSQL for relational data, Qdrant for vector search, and Gemini for embeddings and generation — all containerized with Docker.

This is a 28-day build-in-public project. Each day adds one production-grade layer to the pipeline, documented individually in `/docs`.

---

## Current Status: Day 7 of 28

The full pipeline is live end-to-end: upload a document, and it flows through parsing, chunking, embedding, and semantic search — and you can now chat with it. RAG generation is grounded in retrieved chunks and streamed back to the UI, with conversation turns persisted.

```
upload → S3 store → parse → chunk → embed → search → chat (RAG)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11) |
| Frontend | Next.js 15, Tailwind CSS |
| Relational DB | PostgreSQL 16 |
| Vector DB | Qdrant |
| Object Storage | AWS S3 |
| Embeddings | Gemini `text-embedding-004` (768-dim) |
| Generation | Gemini 2.5 Flash (streaming) |
| Auth | JWT (access + refresh tokens) |
| Orchestration | LangGraph *(coming Day 15+)* |
| Containerization | Docker, Docker Compose |
| Deployment target | Kubernetes, AWS *(Days 24–28)* |

---

## Features Implemented So Far

- **Day 1** — Project scaffold: Docker Compose, FastAPI skeleton, Next.js app shell
- **Day 2** — JWT authentication (access + refresh tokens), PostgreSQL setup, Alembic migrations
- **Day 3** — Document upload pipeline: drag-and-drop UI, S3 storage, presigned URLs, file validation
- **Day 4** — Document parsing: PDF (PyMuPDF), DOCX (python-docx), TXT, CSV → clean extracted text
- **Day 5** — Text chunking: recursive character splitter, page-aware, 512-token chunks with 64-token overlap
- **Day 6** — Embeddings + vector search: Gemini embeddings, Qdrant storage, semantic search API with user isolation
- **Day 7** — RAG generation: Gemini 2.5 Flash answers grounded in retrieved chunks, streamed to the frontend; chat messages persisted to PostgreSQL (`ChatMessage` model + migration); chat dashboard page on the frontend

---

## Project Structure

```
NEXUS-AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/        # auth, documents, chunks, search, chat
│   │   │   └── router.py
│   │   ├── core/                 # config, database, deps, security
│   │   ├── models/                # SQLAlchemy models (incl. ChatMessage)
│   │   ├── schemas/                # Pydantic schemas (incl. chat)
│   │   └── services/               # business logic (S3, parsing, chunking, embeddings, Qdrant, RAG, generation)
│   ├── alembic/versions/           # DB migrations
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── database/postgres/              # Postgres-specific migration tooling
├── frontend/
│   ├── app/                        # Next.js app router root
│   └── src/
│       ├── app/dashboard/          # upload, documents/[id], search, chat pages
│       └── components/             # DocumentList, ParseStatus, ChunkViewer
├── tests/                          # pytest suite (parsing, chunking, embeddings, RAG)
├── docs/                           # Day-by-day build documentation
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- An AWS account with an S3 bucket
- A free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/sumedChalakh/nexusai-enterprise-platform.git
   cd nexusai-enterprise-platform
   ```

2. Copy environment templates and fill in your credentials:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Fill in: `SECRET_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `GEMINI_API_KEY`

3. Run database migrations:
   ```bash
   docker-compose run backend alembic upgrade head
   ```

4. Start all services:
   ```bash
   docker-compose up --build
   ```

   | Service | URL |
   |---|---|
   | Backend API | http://localhost:8000 |
   | API docs (Swagger) | http://localhost:8000/docs |
   | Frontend | http://localhost:3000 |
   | Qdrant dashboard | http://localhost:6333/dashboard |

---

## API Overview

| Endpoint | Description |
|---|---|
| `POST /api/v1/auth/register` | Create a new user |
| `POST /api/v1/auth/login` | Get access + refresh tokens |
| `POST /api/v1/documents/upload` | Upload a document (triggers full pipeline) |
| `GET  /api/v1/documents/` | List user's documents |
| `GET  /api/v1/documents/{id}/status` | Poll processing status |
| `GET  /api/v1/documents/{id}/chunks/` | List chunks for a document |
| `GET  /api/v1/documents/{id}/chunks/stats` | Chunk statistics |
| `POST /api/v1/search/` | Semantic search across documents |
| `POST /api/v1/chat/` | Send a message, get a streamed RAG-grounded answer (persisted to chat history) |

Full interactive documentation available at `/docs` once the backend is running.

---

## Running Tests

```bash
docker-compose run backend pytest tests/ -v
```

---

## Roadmap

| Day(s) | Milestone |
|---|---|
| 1–7 | ✅ Ingestion pipeline + RAG generation (upload, parse, chunk, embed, search, chat) |
| 8–10 | Hybrid search, reranking, citations |
| 11–14 | Conversational memory (Redis), multi-tenant user isolation, test coverage |
| 15–20 | LangGraph multi-agent system (PDF agent, SQL agent, web agent, router) |
| 21–23 | Admin panel, Docker hardening, CI/CD |
| 24–28 | AWS deployment, Kubernetes, observability (Prometheus, Grafana, Loki) |

---

## License

Personal portfolio project. Not licensed for production use without modification.

## Author

**Sumed Chalakh** — ML Engineer | [GitHub](https://github.com/sumedChalakh)