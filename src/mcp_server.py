import contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from mcp.server.fastmcp import FastMCP

from config import API_KEYS, QDRANT_URL, DENSE_MODEL, SPARSE_MODEL
from agent.tools.doc_search import InternalDocSearchTool

# 요청별 user_roles를 저장하는 컨텍스트 변수
_user_roles: contextvars.ContextVar[list[str]] = contextvars.ContextVar("user_roles", default=["all"])


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth = request.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip()
        roles = API_KEYS.get(token)
        if roles is None:
            return Response("Unauthorized", status_code=401, media_type="text/plain")
        reset = _user_roles.set(roles)
        try:
            return await call_next(request)
        finally:
            _user_roles.reset(reset)


mcp = FastMCP("company-knowledge-base")

_search_tool = InternalDocSearchTool(
    qdrant_url=QDRANT_URL,
    dense_model_name=DENSE_MODEL,
    sparse_model_name=SPARSE_MODEL,
)


@mcp.tool(description="사내 문서(규정, 가이드, 프로세스 등)를 검색합니다. 업무 규정, 사규, 프로세스 등 사내 정보를 찾을 때 사용하세요.")
async def search_docs(query: str) -> list[dict]:
    user_roles = _user_roles.get()
    return await _search_tool._arun(
        query=query,
        config={"configurable": {"user_roles": user_roles}},
    )


def create_mcp_app():
    """FastAPI에 마운트할 MCP ASGI 앱을 반환합니다."""
    asgi_app = mcp.streamable_http_app()
    asgi_app.add_middleware(AuthMiddleware)
    return asgi_app
