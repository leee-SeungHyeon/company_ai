# 사내 AI 어시스턴트

사규 Q&A, 이메일 작성 등 업무 생산성을 높여주는 사내 AI 플랫폼입니다.

## 기능

| 기능 | 설명 |
|------|------|
| **사규 Q&A** | 사내 문서(Notion, Confluence, OneDrive)를 기반으로 규정/프로세스 질문에 답변 |
| **이메일 작성** | 요청 내용을 입력하면 격식체 비즈니스 이메일 자동 생성 |

## 구조

```
company_ai/
├── src/
│   ├── api/
│   │   ├── main.py               # FastAPI 진입점
│   │   └── routers/
│   │       ├── qa.py             # 사규 Q&A API
│   │       └── email.py          # 이메일 작성 API
│   ├── agent/
│   │   ├── graph.py              # ReAct Agent (LangGraph)
│   │   ├── llm.py                # LLM 팩토리 (Gemini / OpenAI / Anthropic)
│   │   ├── prompt.py             # 시스템 프롬프트
│   │   ├── state.py              # Agent 상태 정의
│   │   └── tools/
│   │       ├── base.py           # 벡터 검색 기반 클래스
│   │       └── doc_search.py     # 사내 문서 검색 Tool
│   ├── services/
│   │   ├── qa.py                 # Q&A 비즈니스 로직
│   │   └── email.py              # 이메일 작성 로직
│   ├── ingest/
│   │   ├── base.py               # BaseReader 추상 클래스
│   │   ├── notion.py             # Notion Reader
│   │   ├── confluence.py         # Confluence Reader
│   │   ├── onedrive.py           # OneDrive Reader
│   │   └── upload.py             # Qdrant 적재 스크립트
│   ├── chunker/
│   │   └── token.py              # 텍스트 청킹
│   └── config.py                 # 환경 변수 관리
├── static/
│   ├── index.html                # 메인 페이지
│   ├── css/style.css
│   └── js/app.js
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 시작하기

### 1. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 필요한 값을 채웁니다.

**필수 항목**

```env
LLM_PROVIDER=gemini        # gemini | openai | anthropic
LLM_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your-key    # LLM_PROVIDER에 맞는 API 키
```

**문서 소스별 항목 (사용할 소스만 입력)**

```env
# Notion
NOTION_TOKEN=
NOTION_DATABASE_ID=

# Confluence
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your@email.com
CONFLUENCE_API_TOKEN=
CONFLUENCE_SPACE_KEY=

# OneDrive
ONEDRIVE_CLIENT_ID=
ONEDRIVE_CLIENT_SECRET=
ONEDRIVE_TENANT_ID=
```

### 2. 문서 적재 (사규 Q&A 사용 시)

```bash
# Notion 문서 적재
python src/ingest/upload.py --source notion

# Confluence 문서 적재
python src/ingest/upload.py --source confluence

# OneDrive 문서 적재
python src/ingest/upload.py --source onedrive

# 기존 데이터 초기화 후 재적재
python src/ingest/upload.py --source notion --reset
```

### 3. 실행

**Docker (권장)**

```bash
docker compose up -d
```

브라우저에서 `http://localhost:8000` 접속

**로컬 실행**

```bash
pip install .
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## LLM 변경

`.env`에서 `LLM_PROVIDER`와 `LLM_MODEL`만 바꾸면 됩니다.

```env
# Gemini
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash

# OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Anthropic
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022
```

## API

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/qa` | 사규 Q&A |
| `POST` | `/api/email` | 이메일 작성 |

**사규 Q&A**
```json
// Request
{ "query": "연차 사용 규정이 어떻게 되나요?" }

// Response
{ "answer": "..." }
```

**이메일 작성**
```json
// Request
{ "request": "김철수 팀장님께 다음 주 회의 일정 변경 요청 메일" }

// Response
{ "subject": "회의 일정 변경 요청", "body": "안녕하십니까. ..." }
```
