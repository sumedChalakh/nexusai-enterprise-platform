# NexusAI — Enterprise Knowledge Platform

> Multi-agent RAG platform. Upload documents. Chat with your knowledge base. Built in 28 days.

## Stack
- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Next.js 15 + TypeScript + TailwindCSS
- **AI**: Gemini 2.5 Flash + LangGraph + Qdrant
- **DB**: PostgreSQL 16 + Redis 7
- **Infra**: Docker → Kubernetes → AWS

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sumedChalakh/nexusai-enterprise-platform.git
cd nexusai-enterprise-platform

# 2. Env
cp .env.example .env
# edit .env with your keys

# 3. Run
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Build Progress
- [x] Day 1 — Project setup, Docker, FastAPI, Next.js
- [ ] Day 2 — Authentication (JWT + PostgreSQL)
- [ ] Day 3 — File Upload (AWS S3)
- [ ] ...

## Author
Sumed Chalakh — github.com/sumedChalakh
