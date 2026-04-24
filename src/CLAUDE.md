---
paths:
  - "src/api/**/*.py"
  - "src/agent/**/*.py"
  - "src/services/**/*.py"
  - "src/ingest/**/*.py"
---

# Backend — src/CLAUDE.md

## Tech Stack
- FastAPI + uvicorn
- LangGraph (ReAct Agent)
- LangChain (LLM 추상화 — OpenAI / Gemini / Anthropic 지원)
- Qdrant (벡터 DB, hybrid search: dense + sparse BM25)
- FastMCP (MCP 서버)

## LangGraph Agent Pattern
`agent/graph.py`의 워크플로:
```
START → llm_node → (tool_calls?) → execute_tool_node → llm_node → END
```
- `MAX_EXECUTE_TOOL_COUNT`: 툴 최대 실행 횟수 (기본 3회), 초과 시 강제 종료
- 상태: `agent/state.py`의 `State`, `Config` 참조

## Adding a New Tool
1. `src/agent/tools/` 에 새 파일 생성
2. `@tool` 데코레이터 사용, `config: RunnableConfig` 파라미터로 `user_roles` 접근
3. `src/services/qa.py`에서 tools 리스트에 추가

## Adding a New Ingest Source
1. `src/ingest/base.py`의 `BaseReader` 상속
2. `read() -> list[dict]` 구현 (각 dict: `{"text": ..., "metadata": {...}}`)
3. `src/ingest/upload.py`에 `--source` 옵션 추가

## Auth Flow
`src/api/auth.py`: `Authorization: Bearer <api-key>` → `API_KEYS` dict 조회 → `user_roles` 반환
역할이 없으면 403.

## Important Rules
- 환경 변수는 반드시 `from config import ...` 로 사용 (직접 `os.getenv` 금지)
- LLM 인스턴스는 `agent/llm.py`의 `get_llm()` / `get_embeddings()` 사용
- Qdrant 검색 필터: `agent/tools/base.py`의 `build_filter()` 참조, ACL 로직 변경 금지
