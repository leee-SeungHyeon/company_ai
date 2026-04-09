import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import qa
from mcp_server import create_mcp_app

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="사내 지식 베이스")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qa.router, prefix="/api")
app.mount("/mcp", create_mcp_app())
