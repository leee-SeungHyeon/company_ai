import logging
import asyncio
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from qdrant_client import AsyncQdrantClient, models
from fastembed import SparseTextEmbedding
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tqdm import tqdm

logger = logging.getLogger(__name__)


class VectorSearchInput(BaseModel):
    query: str = Field(description="검색할 쿼리입니다.")
    top_k: int = Field(description="반환할 문서 수입니다.", default=5)


class VectorSearchTool(BaseTool):
    name: str = "vector_search"
    description: str = "문서를 검색하는 도구입니다."
    args_schema: Type[BaseModel] = VectorSearchInput
    return_direct: bool = False

    vectorstore: object
    dense_model: object
    sparse_model: object
    dense_vector_size: int
    collection_name: str

    def __init__(self, qdrant_url: str, dense_model_name: str, sparse_model_name: str, collection_name: str = "internal_docs"):
        dense_model = GoogleGenerativeAIEmbeddings(model=dense_model_name)
        sparse_model = SparseTextEmbedding(model_name=sparse_model_name)
        vector_size = len(dense_model.embed_query("test"))
        super().__init__(
            vectorstore=AsyncQdrantClient(url=qdrant_url),
            dense_model=dense_model,
            sparse_model=sparse_model,
            dense_vector_size=vector_size,
            collection_name=collection_name,
        )

    async def upload_documents(self, documents: list[dict], vector_field: str = "content", create_collection: bool = False):
        if create_collection:
            await self.vectorstore.recreate_collection(
                collection_name=self.collection_name,
                vectors_config={"dense": models.VectorParams(size=self.dense_vector_size, distance=models.Distance.COSINE)},
                sparse_vectors_config={"sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)},
            )

        vector_contents = [doc[vector_field] for doc in documents]
        dense_vectors = self._batch_embed(vector_contents, batch_size=64)
        sparse_vectors = list(self.sparse_model.embed(vector_contents))

        points = [
            models.PointStruct(
                id=idx,
                vector={"dense": dense_vector, "sparse": sparse_vector.as_object()},
                payload=dict(doc),
            )
            for idx, (dense_vector, sparse_vector, doc) in enumerate(zip(dense_vectors, sparse_vectors, documents))
        ]

        await self.vectorstore.upsert(collection_name=self.collection_name, points=points)

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        return asyncio.run(self._arun(query))

    async def _arun(
        self,
        query: str,
        top_k: int = 5,
        config: Optional[RunnableConfig] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        dense_vector = await self.dense_model.aembed_query(query)
        sparse_vector = next(self.sparse_model.query_embed(query))

        result = await self.vectorstore.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            prefetch=[
                models.Prefetch(query=dense_vector, using="dense", limit=top_k * 2),
                models.Prefetch(query=sparse_vector.as_object(), using="sparse", limit=top_k * 2),
            ],
            limit=top_k,
        )

        return [{**point.payload, "similarity_score": point.score} for point in result.points]

    def _batch_embed(self, texts: list[str], batch_size: int) -> list:
        total_batches = (len(texts) + batch_size - 1) // batch_size
        logger.info(f"임베딩 생성 중... (총 {len(texts)}개, {total_batches}개 배치)")
        vectors = []
        for i in tqdm(range(0, len(texts), batch_size), desc="임베딩", total=total_batches, unit="batch"):
            vectors.extend(self.dense_model.embed_documents(texts[i:i + batch_size]))
        logger.info(f"임베딩 완료: {len(vectors)}개 벡터 생성")
        return vectors
