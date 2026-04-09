# 사내 지식 베이스

MCP 기반 권한관리가 도입된 RAG 용 사내 지식 베이스입니다.

## 구조

```
company_ai/
├── src/
│   ├── api/
│   │   ├── main.py               # FastAPI 진입점
│   │   ├── auth.py               # API Key 인증
│   │   └── routers/
│   │       └── qa.py             # Q&A REST API (테스트용)
│   ├── agent/
│   │   ├── graph.py              # ReAct Agent (LangGraph)
│   │   ├── llm.py                # LLM 팩토리 (Gemini / OpenAI / Anthropic)
│   │   ├── prompt.py             # 시스템 프롬프트
│   │   ├── state.py              # Agent 상태 정의
│   │   └── tools/
│   │       ├── base.py           # 벡터 검색 기반 클래스 (ACL 필터 포함)
│   │       └── doc_search.py     # 사내 문서 검색 Tool
│   ├── services/
│   │   └── qa.py                 # Q&A 비즈니스 로직
│   ├── ingest/
│   │   ├── base.py               # BaseReader 추상 클래스
│   │   ├── notion.py             # Notion Reader
│   │   ├── confluence.py         # Confluence Reader
│   │   ├── onedrive.py           # OneDrive Reader
│   │   └── upload.py             # Qdrant 적재 스크립트
│   ├── chunker/
│   │   └── token.py              # 텍스트 청킹
│   ├── mcp_server.py             # MCP 서버 (FastMCP)
│   └── config.py                 # 환경 변수 관리
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 시작하기

### 1. 환경 변수 설정

```bash
cp .env.example .env
```

**필수 항목**

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-key

# API Key → roles 매핑
API_KEYS={"my-secret-key": ["hr", "all"], "finance-key": ["finance", "all"]}
```

### 2. 서버 실행

```bash
docker compose up -d
```

### 3. 문서 적재

```bash
# 전체 공개 문서
uv run python src/ingest/upload.py --source notion --roles all --reset

# HR 팀만 접근 가능한 문서
uv run python src/ingest/upload.py --source confluence --roles hr,all
```

### 4. Claude Desktop 연결 (MCP)

`~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "company-kb": {
      "url": "http://localhost:8000/mcp",
      "headers": { "Authorization": "Bearer my-secret-key" }
    }
  }
}
```

## API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/qa` | Q&A (테스트용) |
| `*`    | `/mcp`    | MCP 서버 엔드포인트 |

**Q&A 테스트**
```bash
curl -X POST http://localhost:8000/api/qa \
  -H "Authorization: Bearer my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "연차 사용 규정이 어떻게 되나요?"}'
```

## 권한 동작

```
API Key → roles 조회 → Qdrant payload_filter 적용 → 허용된 문서만 검색
```

문서 적재 시 `--roles` 로 지정한 역할만 해당 문서에 접근 가능합니다.
