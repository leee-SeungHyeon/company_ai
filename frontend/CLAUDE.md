@AGENTS.md

# Frontend — CLAUDE.md

## Tech Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS

## Key Commands
```bash
npm run dev    # 개발 서버 (http://localhost:3000)
npm run build  # 프로덕션 빌드
npm run lint   # ESLint
```

## API Integration
백엔드 FastAPI (기본 `http://localhost:8000`):
- `POST /api/qa` — 일반 Q&A
- `POST /api/qa/stream` — SSE 스트리밍 응답
- `Authorization: Bearer <api-key>` 헤더 필수

스트리밍은 `text/event-stream` (SSE) 방식.

## Project Structure
```
frontend/
├── app/          # Next.js App Router 페이지
├── hooks/        # 커스텀 React 훅
└── ...
```

## Important Rules
- API base URL은 환경 변수(`NEXT_PUBLIC_API_URL`)로 관리
- Bearer 토큰은 환경 변수(`NEXT_PUBLIC_API_KEY`)로 관리, 코드에 하드코딩 금지
- 스트리밍 응답 처리 시 `hooks/` 의 기존 훅 재사용 우선
