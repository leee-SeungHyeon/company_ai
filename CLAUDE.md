# Company AI

MCP 기반 권한관리(ACL)가 적용된 **사내 지식 베이스 RAG 시스템**.

## Architecture
```
Next.js UI (3000) → FastAPI (8000) → LangGraph ReAct Agent → Qdrant (6333)
                                 └── FastMCP (/mcp endpoint)
```

## Key Commands

### Backend
```bash
uv sync                                     # 의존성 설치
docker compose up qdrant -d                 # Qdrant 기동 (필수)
PYTHONPATH=src uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
uv run python src/ingest/upload.py --source local --path ./docs --roles all --reset
```

### Frontend
```bash
cd frontend && npm install && npm run dev   # http://localhost:3000
```

자주 쓰는 워크플로는 슬래시 명령으로 — `/qdrant-up`, `/serve`, `/ingest`, `/qa-test`, `/qdrant-status`.

## Environment Variables
`.env.example` 참조. 필수:
- `LLM_PROVIDER` — `openai` | `gemini` | `anthropic`
- `LLM_MODEL` — 모델명
- `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY`
- `API_KEYS` — JSON: `{"<api-key>": ["role1", "role2"]}` (Bearer → roles 매핑)
- `QDRANT_URL` — 기본 `http://localhost:6333`
- `DENSE_MODEL` — 임베딩 모델명

## ACL 시스템 (핵심 차별점)
```
Authorization: Bearer <api-key>
  → API_KEYS dict 조회 (config.py)
  → user_roles 를 LangGraph configurable 로 전달
  → build_filter(user_roles) → Qdrant payload_filter
  → 허용 roles 가진 문서만 검색
```
적재 시 `--roles` 로 접근 역할 지정. `all` 은 전체 공개.

## Code Conventions
- Python import 기준: `PYTHONPATH=src` (예: `from api.xxx`, `from agent.xxx`).
- 실행은 항상 `uv run`.
- 백엔드는 전부 `async/await`.
- LangGraph 상태 전환은 `Command(update=..., goto=...)` 패턴.
- 환경변수는 `src/config.py` 에서만 읽는다 — 직접 `os.getenv` 금지.

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
@.claude/rules/langgraph.md
