"""
사내 문서를 Qdrant에 적재하는 스크립트입니다.

사용 예시:
    python src/ingest/upload.py --source notion
    python src/ingest/upload.py --source confluence --reset
    python src/ingest/upload.py --source onedrive
"""
import asyncio
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from chunker.token import TokenSizeChunker
from agent.tools.doc_search import InternalDocSearchTool
from ingest.notion import NotionReader
from ingest.confluence import ConfluenceReader
from ingest.onedrive import OneDriveReader
from ingest.local import LocalReader
from config import QDRANT_URL, DENSE_MODEL, SPARSE_MODEL

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def upload(reader, reset: bool = False):
    tool = InternalDocSearchTool(qdrant_url=QDRANT_URL, dense_model_name=DENSE_MODEL, sparse_model_name=SPARSE_MODEL)
    chunker = TokenSizeChunker(chunk_size=1000, chunk_overlap=200)

    logger.info("문서 로드 중...")
    documents = reader.load()
    logger.info(f"{len(documents)}개 문서 로드 완료")

    all_chunks = []
    for doc in documents:
        chunks = chunker(doc["content"], metadata={
            "title": doc.get("title", ""),
            "source": doc["source"],
            "file_type": doc["file_type"],
            "allowed_roles": doc.get("allowed_roles", ["all"]),
        })
        all_chunks.extend(chunks)

    logger.info(f"총 {len(all_chunks)}개 청크 생성")
    await tool.upload_documents(all_chunks, create_collection=reset)
    logger.info("Qdrant 업로드 완료")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["notion", "confluence", "onedrive", "local"], required=True)
    parser.add_argument("--path", help="로컬 파일 또는 디렉토리 경로 (--source local 시 필수)")
    parser.add_argument("--reset", action="store_true", help="기존 컬렉션 초기화 후 재적재")
    parser.add_argument("--roles", default="all", help="접근 허용 역할 (쉼표 구분, 예: hr,manager)")
    args = parser.parse_args()

    if args.source == "local" and not args.path:
        parser.error("--source local 사용 시 --path 가 필요합니다.")

    allowed_roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    readers = {
        "notion": lambda: NotionReader(allowed_roles=allowed_roles),
        "confluence": lambda: ConfluenceReader(allowed_roles=allowed_roles),
        "onedrive": lambda: OneDriveReader(allowed_roles=allowed_roles),
        "local": lambda: LocalReader(path=args.path, allowed_roles=allowed_roles),
    }
    asyncio.run(upload(readers[args.source](), reset=args.reset))


if __name__ == "__main__":
    main()
