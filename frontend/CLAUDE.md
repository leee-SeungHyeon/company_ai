@AGENTS.md

# Frontend (frontend/)

## Tech Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS

## Key Commands
```bash
npm run dev    # http://localhost:3000
npm run build  # 프로덕션 빌드
npm run lint   # ESLint
```

## Backend Integration
FastAPI 기본: `http://localhost:8000`
- `POST /api/qa` — 일반 Q&A
- `POST /api/qa/stream` — SSE 스트리밍 (`text/event-stream`)
- 모든 요청에 `Authorization: Bearer <api-key>` 필수

## Project Structure
```
frontend/
├── app/      # Next.js App Router 페이지
├── hooks/    # 커스텀 React 훅
└── ...
```

## Important Rules
- API base URL 은 `NEXT_PUBLIC_API_URL` 환경변수로 관리.
- Bearer 토큰은 `NEXT_PUBLIC_API_KEY` 환경변수로 관리, **코드 하드코딩 금지**.
- 스트리밍 응답 처리는 `hooks/` 기존 훅 재사용 우선.
