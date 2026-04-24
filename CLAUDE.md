# Company AI — CLAUDE.md

## Project Overview
MCP 기반 권한관리가 적용된 사내 지식 베이스 RAG 시스템.
FastAPI 백엔드 + LangGraph ReAct Agent + Qdrant 벡터 DB + Next.js 챗봇 UI.

## Architecture
```
Next.js UI → FastAPI (8000) → LangGraph ReAct Agent → Qdrant (6333)
                         └── MCP Server (/mcp endpoint)
```

## Key Commands

### Backend
```bash
# 의존성 설치
uv sync

# Qdrant 실행 (필수)
docker compose up qdrant -d

# 백엔드 서버
PYTHONPATH=src uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 문서 적재
uv run python src/ingest/upload.py --source local --path ./docs --roles all --reset
```

### Frontend
```bash
cd frontend && npm install && npm run dev  # http://localhost:3000
```

## Environment Variables
`.env.example` 참조. 필수 항목:
- `LLM_PROVIDER` — `openai` | `gemini` | `anthropic`
- `LLM_MODEL` — 모델명
- `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY`
- `API_KEYS` — JSON: `{"key": ["role1", "role2"]}` (권한 매핑)
- `QDRANT_URL` — 기본값 `http://localhost:6333`
- `DENSE_MODEL` — 임베딩 모델명

## ACL (Access Control) System
```
API Key → roles 조회 (config.py) → Qdrant payload_filter → 허용 문서만 반환
```
- 문서 적재 시 `--roles` 파라미터로 접근 가능 역할 지정
- `all` 역할은 전체 공개 문서

## Code Conventions
- Python: `PYTHONPATH=src` 기준으로 import (`from api.xxx`, `from agent.xxx`)
- Python 실행: 항상 `uv run` 사용
- 비동기: 백엔드 전체 `async/await` 기반
- LangGraph: `Command(update=..., goto=...)` 패턴으로 상태 전환
- 환경 변수: `src/config.py`에서 중앙 관리, 직접 `os.getenv` 사용 금지

## Project Structure
```
src/
├── api/          # FastAPI 진입점, 라우터, 인증
├── agent/        # LangGraph ReAct Agent, LLM 팩토리, 툴
├── services/     # 비즈니스 로직
├── ingest/       # 문서 적재 (local, Notion, Confluence, OneDrive)
├── chunker/      # 텍스트 청킹
├── mcp_server.py # FastMCP 서버
└── config.py     # 환경 변수 중앙 관리
frontend/         # Next.js 챗봇 UI
docs/             # 테스트용 사내 문서
```

@src/CLAUDE.md
@frontend/CLAUDE.md
@.claude/rules/acl.md
@.claude/rules/ingest.md
