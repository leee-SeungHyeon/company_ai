from typing import Type
from pydantic import BaseModel, Field
from .base import VectorSearchInput, VectorSearchTool


class InternalDocSearchInput(VectorSearchInput):
    query: str = Field(description="사내 문서에서 검색할 쿼리입니다. 영어로 입력하면 더 정확합니다.")


class InternalDocSearchTool(VectorSearchTool):
    name: str = "internal_doc_search"
    description: str = (
        "사내 문서(규정, 가이드, 프로세스 등)를 검색하는 도구입니다. "
        "업무 규정, 사규, 프로세스 등 사내 정보를 찾을 때 사용하세요."
    )
    args_schema: Type[BaseModel] = InternalDocSearchInput

    def __init__(self, *args, **kwargs):
        super().__init__(collection_name="internal_docs", **kwargs)
