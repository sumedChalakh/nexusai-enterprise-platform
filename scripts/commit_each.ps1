# ============================================================
# NEXUS-AI: Granular commit script - one commit per change
# ============================================================
Set-Location "c:\Users\ACER\Desktop\NEXUS-AI"

function Do-Commit {
    param([string[]]$Files, [string]$Message)
    foreach ($f in $Files) { git add -- $f 2>$null }
    $st = & git status --short
    if ($st) {
        git commit -m $Message
        Write-Host "OK: $Message" -ForegroundColor Green
    } else {
        Write-Host "SKIP (nothing staged): $Message" -ForegroundColor Yellow
    }
}

# 1. Config & environment
Do-Commit -Files ".env.example"                                            -Message "chore: update environment variable template"
Do-Commit -Files "backend/config.py"                                       -Message "config: update backend configuration settings"
Do-Commit -Files "backend/app/core/config.py"                              -Message "config: update core application config"

# 2. Database layer
Do-Commit -Files "backend/database.py"                                     -Message "db: update legacy database module"
Do-Commit -Files "backend/app/core/database.py"                            -Message "db: add core database connection module"
Do-Commit -Files "backend/app/core/db.py"                                  -Message "db: add SQLAlchemy session factory"
Do-Commit -Files "backend/alembic/versions/001_users.py"                   -Message "db: add alembic migration - users table"
Do-Commit -Files "backend/alembic/versions/007_chat_sessions.py"           -Message "db: add alembic migration - chat sessions table"

# 3. Models
Do-Commit -Files "backend/app/models/__init__.py"                          -Message "models: add models package init"
Do-Commit -Files "backend/app/models/user.py"                              -Message "models: add User ORM model"
Do-Commit -Files "backend/app/models/chat_session.py"                      -Message "models: add ChatSession ORM model"

# 4. Schemas
Do-Commit -Files "backend/app/schemas/__init__.py"                         -Message "schemas: add schemas package init"
Do-Commit -Files "backend/app/schemas/auth.py"                             -Message "schemas: add auth request/response schemas"

# 5. Core utilities
Do-Commit -Files "backend/app/core/__init__.py"                            -Message "core: add core package init"
Do-Commit -Files "backend/app/core/auth.py"                                -Message "core: add JWT authentication utilities"
Do-Commit -Files "backend/app/core/deps.py"                                -Message "core: add FastAPI dependency injection helpers"
Do-Commit -Files "backend/app/core/logging.py"                             -Message "core: add structured logging configuration"
Do-Commit -Files "backend/app/core/llm.py"                                 -Message "core: add LLM client initialisation"
Do-Commit -Files "backend/app/core/embeddings.py"                          -Message "core: add embedding model initialisation"
Do-Commit -Files "backend/app/core/qdrant.py"                              -Message "core: add Qdrant client initialisation"

# 6. Auth service
Do-Commit -Files "backend/app/services/__init__.py"                        -Message "services: add services package init"
Do-Commit -Files "backend/app/services/auth_service.py"                    -Message "feat: add user authentication service"

# 7. Auth endpoint
Do-Commit -Files "backend/app/__init__.py"                                 -Message "api: add app package init"
Do-Commit -Files "backend/app/api/__init__.py"                             -Message "api: add api package init"
Do-Commit -Files "backend/app/api/v1/__init__.py"                          -Message "api: add v1 package init"
Do-Commit -Files "backend/app/api/v1/endpoints/__init__.py"                -Message "api: add endpoints package init"
Do-Commit -Files "backend/app/api/v1/endpoints/auth.py"                    -Message "feat: add /auth login and register endpoints"

# 8. Admin
Do-Commit -Files "backend/app/services/admin_service.py"                   -Message "feat: add admin management service"
Do-Commit -Files "backend/app/api/v1/endpoints/admin.py"                   -Message "feat: add /admin endpoints"

# 9. Documents endpoint (modified)
Do-Commit -Files "backend/app/api/v1/endpoints/documents.py"               -Message "feat: update documents endpoint with user isolation"

# 10. Chat sessions
Do-Commit -Files "backend/app/services/chat_history_service.py"            -Message "feat: add chat history persistence service"
Do-Commit -Files "backend/app/api/v1/endpoints/chat_sessions.py"           -Message "feat: add /chat-sessions CRUD endpoints"

# 11. Hybrid search
Do-Commit -Files "backend/app/services/hybrid_search_service.py"           -Message "feat: add hybrid BM25 + vector search service"
Do-Commit -Files "backend/app/api/v1/endpoints/hybrid_search.py"           -Message "feat: add /hybrid-search endpoint"

# 12. Citations
Do-Commit -Files "backend/app/services/citation_service.py"                -Message "feat: add source citation extraction service"
Do-Commit -Files "backend/app/api/v1/endpoints/citations.py"               -Message "feat: add /citations endpoint"

# 13. Reranking
Do-Commit -Files "backend/app/services/reranker_service.py"                -Message "feat: add cross-encoder reranking service"
Do-Commit -Files "backend/app/api/v1/endpoints/reranking.py"               -Message "feat: add /reranking endpoint"

# 14. User isolation
Do-Commit -Files "backend/app/services/user_isolation_service.py"          -Message "feat: add per-user data isolation service"

# 15. Conversational memory
Do-Commit -Files "backend/app/services/conv_memory_service.py"             -Message "feat: add conversational memory service"

# 16. Metrics
Do-Commit -Files "backend/app/services/metrics.py"                         -Message "feat: add Prometheus metrics collection"

# 17. Existing services (modified)
Do-Commit -Files "backend/app/services/embedding_service.py"               -Message "refactor: update embedding service"
Do-Commit -Files "backend/app/services/parser_service.py"                  -Message "refactor: update parser service"
Do-Commit -Files "backend/app/services/processing_service.py"              -Message "refactor: update document processing service"
Do-Commit -Files "backend/app/services/qdrant_service.py"                  -Message "refactor: update Qdrant vector store service"
Do-Commit -Files "backend/app/services/s3_service.py"                      -Message "refactor: update S3 storage service"

# 18. Agent framework
Do-Commit -Files "backend/app/services/agents"                             -Message "feat: add multi-agent framework (LangGraph)"
Do-Commit -Files "backend/app/api/v1/endpoints/agent.py"                   -Message "feat: add /agent single-agent endpoint"
Do-Commit -Files "backend/app/api/v1/endpoints/agent_multi.py"             -Message "feat: add /agent/multi multi-agent endpoint"
Do-Commit -Files "backend/app/api/v1/endpoints/agent_pdf.py"               -Message "feat: add /agent/pdf PDF-specialist endpoint"
Do-Commit -Files "backend/app/api/v1/endpoints/agent_sql.py"               -Message "feat: add /agent/sql SQL-agent endpoint"
Do-Commit -Files "backend/app/api/v1/endpoints/agent_web.py"               -Message "feat: add /agent/web web-search agent endpoint"

# 19. Backend init and dependencies
Do-Commit -Files "backend/__init__.py"                                     -Message "chore: add backend package init"
Do-Commit -Files "backend/dependencies.py"                                 -Message "refactor: update backend dependencies module"

# 20. Router and main
Do-Commit -Files "backend/app/api/v1/router.py"                            -Message "feat: update API router - register all v1 routes"
Do-Commit -Files "backend/app/main.py"                                     -Message "feat: add new FastAPI application entry point"
Do-Commit -Files "backend/main.py"                                         -Message "refactor: update legacy main entry point"

# 21. Requirements
Do-Commit -Files "backend/requirements.txt"                                -Message "chore: update Python dependencies"

# 22. Backend Dockerfile
Do-Commit -Files "backend/Dockerfile"                                      -Message "docker: update backend Dockerfile"

# 23. Test utilities
Do-Commit -Files "backend/test_upload.py"                                  -Message "test: add upload integration test script"
Do-Commit -Files "backend/test_doc.txt"                                    -Message "test: add sample test document"

# 24. Standalone services
Do-Commit -Files "services/__init__.py"                                    -Message "feat: add standalone services package init"
Do-Commit -Files "services/auth_service"                                   -Message "feat: add standalone auth microservice"

# 25. Frontend - remove old TypeScript files
Do-Commit -Files "frontend/app/layout.tsx"                                 -Message "refactor: remove old TS layout (replaced by JSX)"
Do-Commit -Files "frontend/app/page.tsx"                                   -Message "refactor: remove old TS home page (replaced by JSX)"
Do-Commit -Files "frontend/src/app/dashboard/chat/page.jsx"                -Message "refactor: remove old dashboard chat page"
Do-Commit -Files "frontend/src/app/dashboard/documents/[id]/page.jsx"     -Message "refactor: remove old document detail page"
Do-Commit -Files "frontend/src/app/dashboard/search/page.jsx"             -Message "refactor: remove old dashboard search page"
Do-Commit -Files "frontend/src/app/dashboard/upload/page.jsx"             -Message "refactor: remove old dashboard upload page"
Do-Commit -Files "frontend/src/components/ChunkViewer.jsx"                -Message "refactor: remove old ChunkViewer component"
Do-Commit -Files "frontend/src/components/DocumentList.jsx"               -Message "refactor: remove old DocumentList component"
Do-Commit -Files "frontend/src/components/ParseStatus.jsx"                -Message "refactor: remove old ParseStatus component"

# 26. Frontend - new entry points
Do-Commit -Files "frontend/app/layout.jsx"                                 -Message "feat: add new root layout (JSX)"
Do-Commit -Files "frontend/app/page.jsx"                                   -Message "feat: add new home page (JSX)"
Do-Commit -Files "frontend/app/globals.css"                                -Message "style: update global CSS styles"
Do-Commit -Files "frontend/next.config.js"                                 -Message "config: update Next.js configuration"
Do-Commit -Files "frontend/postcss.config.js"                              -Message "config: add PostCSS configuration"

# 27. Frontend - components
Do-Commit -Files "frontend/app/components"                                 -Message "feat: add new reusable UI components"

# 28. Frontend - auth pages
Do-Commit -Files "frontend/app/login"                                      -Message "feat: add login page"

# 29. Frontend - dashboard pages
Do-Commit -Files "frontend/app/dashboard"                                  -Message "feat: add new dashboard pages"

# 30. Frontend - public assets
Do-Commit -Files "frontend/public"                                         -Message "assets: add frontend public assets"

# 31. Frontend Dockerfile
Do-Commit -Files "frontend/Dockerfile"                                     -Message "docker: update frontend Dockerfile"

# 32. Docker Compose files
Do-Commit -Files "docker-compose.yml"                                      -Message "docker: update main docker-compose configuration"
Do-Commit -Files "docker-compose.grafana.yml"                              -Message "docker: add Grafana monitoring compose file"
Do-Commit -Files "docker-compose.logging.yml"                              -Message "docker: add centralised logging compose file"
Do-Commit -Files "docker-compose.metrics.yml"                              -Message "docker: add metrics collection compose file"
Do-Commit -Files "docker-compose.hardened.yml"                             -Message "docker: add hardened/production compose file"

# 33. Monitoring stack
Do-Commit -Files "monitoring"                                              -Message "ops: add monitoring stack (Prometheus/Grafana)"

# 34. Kubernetes manifests
Do-Commit -Files "k8s"                                                     -Message "ops: add Kubernetes deployment manifests"

# 35. Scripts
Do-Commit -Files "scripts"                                                 -Message "chore: add utility and deployment scripts"

# 36. GitHub Actions CI/CD
Do-Commit -Files ".github"                                                 -Message "ci: add GitHub Actions workflows"

# 37. App directory
Do-Commit -Files "app"                                                     -Message "feat: add top-level app module"

# 38. Tests
Do-Commit -Files "tests/conftest.py"                                       -Message "test: add pytest fixtures and conftest"
Do-Commit -Files "tests/test_admin.py"                                     -Message "test: add admin endpoint tests"
Do-Commit -Files "tests/test_agent_graph.py"                               -Message "test: add agent graph unit tests"
Do-Commit -Files "tests/test_master_graph.py"                              -Message "test: add master orchestration graph tests"
Do-Commit -Files "tests/test_multi_agent.py"                               -Message "test: add multi-agent integration tests"
Do-Commit -Files "tests/test_pdf_agent.py"                                 -Message "test: add PDF agent tests"
Do-Commit -Files "tests/test_router_agent.py"                              -Message "test: add router agent tests"
Do-Commit -Files "tests/test_sql_agent.py"                                 -Message "test: add SQL agent tests"
Do-Commit -Files "tests/test_sql_tools.py"                                 -Message "test: add SQL tools unit tests"
Do-Commit -Files "tests/test_web_agent.py"                                 -Message "test: add web search agent tests"
Do-Commit -Files "tests/test_metrics.py"                                   -Message "test: add metrics/observability tests"
Do-Commit -Files "tests/test_day8_14_features.py"                          -Message "test: add day-8 to day-14 feature regression tests"

# 39. Deleted legacy file
Do-Commit -Files "PATCH_user_model.txt"                                    -Message "chore: remove legacy user-model patch notes"

# 40. Root test artifact
Do-Commit -Files "test_doc.txt"                                            -Message "test: add root-level sample test document"

# Push all commits
Write-Host ""
Write-Host "Pushing all commits to origin/main..." -ForegroundColor Cyan
git push origin main
Write-Host "All done!" -ForegroundColor Green
