---
paths:
  - "src/api/**/*.py"
  - "src/agent/**/*.py"
  - "src/services/**/*.py"
  - "src/ingest/**/*.py"
---

# Backend (src/)

## Tech Stack
- FastAPI + uvicorn
- LangGraph (ReAct Agent)
- LangChain (LLM 추상화 — OpenAI / Gemini / Anthropic / vLLM·SGLang)
- Qdrant (hybrid search: dense + sparse BM25)
- FastMCP (MCP 서버)

## LangGraph Agent (`agent/graph.py`)
```
START → llm_node → (tool_calls?) → execute_tool_node → llm_node → END
```
- `MAX_EXECUTE_TOOL_COUNT` (기본 3) 초과 시 강제 종료.
- 상태/설정은 `agent/state.py` 의 `State`, `Config`.
- 자세한 규칙은 `@.claude/rules/langgraph.md` 참조.

## 새 툴 추가
1. `src/agent/tools/` 에 파일 생성.
2. `@tool` 데코레이터 + `config: RunnableConfig` 파라미터로 `user_roles` 접근.
3. `src/services/qa.py` tools 리스트에 등록.

## 새 ingest 소스 추가
규칙은 `@.claude/rules/ingest.md` 참조. 요점:
1. `src/ingest/base.py` 의 `BaseReader` 상속.
2. `read() -> list[dict]` 반환 (`{"text": str, "metadata": {...}}`).
3. `src/ingest/upload.py` 의 `--source` argparse 옵션 추가.

## Auth Flow
`src/api/auth.py:get_user_roles`: `Authorization: Bearer <api-key>` → `API_KEYS` 조회 → `roles` 반환. 매핑 없으면 401.

## Important Rules
- 환경변수는 반드시 `from config import ...` (직접 `os.getenv` 금지).
- LLM/임베딩 인스턴스는 `agent/llm.py` 의 `get_llm()` / `get_embedding_model()` 사용.
- ACL 핵심(`agent/tools/base.py:VectorSearchTool._arun` 안 query_filter, `api/auth.py:get_user_roles`, `config.py:API_KEYS`) 변경 금지. 상세는 `@.claude/rules/acl.md`.
- ACL 회귀 테스트: `uv run pytest tests/test_acl.py`.
