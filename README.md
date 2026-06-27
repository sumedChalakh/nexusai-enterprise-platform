# NexusAI — Multi-Agent RAG Enterprise Knowledge Platform

> A production-grade, full-stack AI platform built in 28 days — one feature layer at a time.

NexusAI lets teams upload documents and query them using a **multi-agent RAG pipeline** powered by Gemini, LangGraph, and Qdrant. It ships with JWT auth, per-user data isolation, hybrid search, reranking, citations, conversational memory, Kubernetes manifests, and a full observability stack.

---

## 🚦 Current Status: Day 14 of 28 — Complete

```
upload → S3 → parse → chunk → embed → hybrid search → rerank → cite → multi-agent RAG → stream
```

All 14 days are shipped and running. Every layer is tested, containerised, and CI-gated.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusAI Platform                         │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────────────────────────┐   │
│  │  Next.js 15 │───▶│           FastAPI Backend             │   │
│  │  Frontend   │    │  ┌────────┐ ┌────────┐ ┌──────────┐ │   │
│  └─────────────┘    │  │  Auth  │ │  Docs  │ │  Agents  │ │   │
│                     │  └────────┘ └────────┘ └──────────┘ │   │
│                     │         LangGraph Router              │   │
│                     │   ┌──────┬──────┬──────┬──────────┐  │   │
│                     │   │ RAG  │ PDF  │ SQL  │   Web    │  │   │
│                     │   │Agent │Agent │Agent │  Agent   │  │   │
│                     │   └──────┴──────┴──────┴──────────┘  │   │
│                     └──────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │PostgreSQL│  │  Qdrant  │  │  AWS S3  │  │ Prometheus + │   │
│  │   (auth/ │  │ (vector  │  │(document │  │   Grafana +  │   │
│  │  history)│  │  store)  │  │ storage) │  │    Loki      │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11), Uvicorn |
| Frontend | Next.js 15, Tailwind CSS |
| Relational DB | PostgreSQL 16 + Alembic migrations |
| Vector DB | Qdrant |
| Object Storage | AWS S3 |
| Embeddings | Gemini `text-embedding-004` (768-dim) |
| Generation | Gemini 2.5 Flash (streaming) |
| Agent Orchestration | LangGraph (multi-agent graphs) |
| Hybrid Search | BM25 + dense vector fusion |
| Reranking | Cross-encoder reranker |
| Auth | JWT (access + refresh tokens, bcrypt) |
| Containerisation | Docker, Docker Compose |
| Orchestration | Kubernetes (5 manifest files) |
| CI/CD | GitHub Actions |
| Observability | Prometheus, Grafana, Loki, Promtail |

---

## ✅ Features — Day by Day

| Day | Feature |
|---|---|
| **1** | Project scaffold: Docker Compose, FastAPI skeleton, Next.js app shell |
| **2** | JWT auth (access + refresh tokens), PostgreSQL, Alembic migrations |
| **3** | Document upload: drag-and-drop UI, S3 storage, presigned URLs, file validation |
| **4** | Document parsing: PDF (PyMuPDF), DOCX (python-docx), TXT, CSV |
| **5** | Text chunking: recursive splitter, 512-token chunks, 64-token overlap |
| **6** | Embeddings + vector search: Gemini embeddings, Qdrant, semantic search API with user isolation |
| **7** | RAG generation: Gemini 2.5 Flash answers grounded in retrieved chunks, streamed to UI; chat history persisted |
| **8** | Hybrid search: BM25 + dense vector fusion for improved recall |
| **9** | Cross-encoder reranking: re-score retrieved chunks for precision |
| **10** | Source citations: every answer includes chunk-level provenance |
| **11** | Conversational memory: multi-turn context preserved across sessions |
| **12** | Per-user data isolation: strict namespace scoping across PostgreSQL + Qdrant |
| **13** | LangGraph multi-agent system: Router → RAG / PDF / SQL / Web agents |
| **14** | Admin panel, test coverage, Docker hardening, GitHub Actions CI/CD |

---

## 🗂️ Project Structure

```
NEXUS-AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/          # auth, documents, chat_sessions,
│   │   │   │                       # hybrid_search, reranking, citations,
│   │   │   │                       # agent, agent_multi, agent_pdf,
│   │   │   │                       # agent_sql, agent_web, admin
│   │   │   └── router.py
│   │   ├── core/                   # config, database, deps, auth, llm,
│   │   │                           # embeddings, qdrant, logging
│   │   ├── models/                 # User, ChatSession (SQLAlchemy)
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   └── services/
│   │       ├── agents/             # LangGraph graphs, nodes, state,
│   │       │                       # router_agent, sql_agent, web_agent,
│   │       │                       # multi_agent
│   │       ├── auth_service.py
│   │       ├── admin_service.py
│   │       ├── chat_history_service.py
│   │       ├── citation_service.py
│   │       ├── conv_memory_service.py
│   │       ├── embedding_service.py
│   │       ├── hybrid_search_service.py
│   │       ├── metrics.py
│   │       ├── parser_service.py
│   │       ├── processing_service.py
│   │       ├── qdrant_service.py
│   │       ├── reranker_service.py
│   │       ├── s3_service.py
│   │       └── user_isolation_service.py
│   ├── alembic/versions/           # DB migrations (users, chat sessions)
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── app/
│       ├── components/             # ChunkViewer, DocumentList, ParseStatus
│       ├── dashboard/              # overview, upload, documents/[id],
│       │                           # search, chat pages
│       ├── login/
│       ├── layout.jsx
│       └── page.jsx
├── monitoring/
│   ├── prometheus/prometheus.yml
│   ├── grafana/provisioning/       # dashboards + datasources
│   └── promtail/promtail-config.yml
├── k8s/
│   ├── 00-namespace-config.yaml
│   ├── 01-data-stores.yaml
│   ├── 02-backend.yaml
│   ├── 03-frontend.yaml
│   └── 04-ingress.yaml
├── tests/                          # pytest suite (12 test files)
├── scripts/                        # deploy.sh, nginx.conf, ec2 user-data
├── .github/workflows/ci-cd.yml     # GitHub Actions CI/CD pipeline
├── docker-compose.yml
├── docker-compose.hardened.yml
├── docker-compose.metrics.yml
├── docker-compose.logging.yml
├── docker-compose.grafana.yml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- An AWS account with an S3 bucket
- A Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Local Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/sumedChalakh/nexusai-enterprise-platform.git
   cd nexusai-enterprise-platform
   ```

2. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Fill in: `SECRET_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `GEMINI_API_KEY`

3. **Run database migrations:**
   ```bash
   docker-compose run backend alembic upgrade head
   ```

4. **Start all services:**
   ```bash
   docker-compose up --build
   ```

   | Service | URL |
   |---|---|
   | Backend API | http://localhost:8000 |
   | API Docs (Swagger) | http://localhost:8000/docs |
   | Frontend | http://localhost:3000 |
   | Qdrant Dashboard | http://localhost:6333/dashboard |

### With Monitoring Stack

```bash
docker-compose -f docker-compose.yml -f docker-compose.metrics.yml -f docker-compose.grafana.yml -f docker-compose.logging.yml up --build
```

| Service | URL |
|---|---|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |
| Loki | http://localhost:3100 |

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Get access + refresh tokens |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload` | Upload a document (triggers full pipeline) |
| `GET` | `/api/v1/documents/` | List user's documents |
| `GET` | `/api/v1/documents/{id}/status` | Poll processing status |
| `GET` | `/api/v1/documents/{id}/chunks/` | List chunks |

### Search & RAG
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/search/` | Semantic (dense) search |
| `POST` | `/api/v1/hybrid-search/` | Hybrid BM25 + vector search |
| `POST` | `/api/v1/reranking/` | Rerank a result set |
| `POST` | `/api/v1/citations/` | Extract source citations |

### Agents
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/agent/` | Single RAG agent |
| `POST` | `/api/v1/agent/multi` | Multi-agent orchestrator (LangGraph router) |
| `POST` | `/api/v1/agent/pdf` | PDF specialist agent |
| `POST` | `/api/v1/agent/sql` | SQL query agent |
| `POST` | `/api/v1/agent/web` | Web search agent |

### Chat Sessions
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/chat-sessions/` | List all sessions |
| `POST` | `/api/v1/chat-sessions/` | Create a new session |
| `DELETE` | `/api/v1/chat-sessions/{id}` | Delete a session |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/users` | List all users (admin only) |
| `GET` | `/api/v1/admin/stats` | Platform-wide statistics |

Full interactive docs available at `http://localhost:8000/docs`.

---

## 🧪 Running Tests

```bash
# All tests
docker-compose run backend pytest tests/ -v

# Specific suite
docker-compose run backend pytest tests/test_multi_agent.py -v
docker-compose run backend pytest tests/test_hybrid_search.py -v
```

Test files cover: admin, agent graphs, master graph, multi-agent, PDF agent, router agent, SQL agent, SQL tools, web agent, metrics, day 8–14 features.

---

## ☸️ Kubernetes Deployment

```bash
kubectl apply -f k8s/00-namespace-config.yaml
kubectl apply -f k8s/01-data-stores.yaml
kubectl apply -f k8s/02-backend.yaml
kubectl apply -f k8s/03-frontend.yaml
kubectl apply -f k8s/04-ingress.yaml
```

---

## 🗺️ Roadmap

| Days | Milestone | Status |
|---|---|---|
| 1–7 | Ingestion pipeline + RAG generation | ✅ Done |
| 8–10 | Hybrid search, reranking, citations | ✅ Done |
| 11–14 | Conversational memory, user isolation, multi-agent, CI/CD | ✅ Done |
| 15–20 | Advanced agent capabilities, tool use, streaming | 🔜 Next |
| 21–23 | Docker hardening, production secrets, rate limiting | 🔜 Next |
| 24–28 | AWS deployment, Kubernetes, full observability | 🔜 Next |

---

## 📄 License

Personal portfolio project. Not licensed for production use without modification.

## 👤 Author

**Sumed Chalakh** — ML Engineer | [GitHub](https://github.com/sumedChalakh)