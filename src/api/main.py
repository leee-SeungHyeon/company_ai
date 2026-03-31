import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from api.routers import qa, email

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="사내 AI 어시스턴트")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(qa.router, prefix="/api")
app.include_router(email.router, prefix="/api")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")
