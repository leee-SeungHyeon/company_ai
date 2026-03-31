from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TokenSizeChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: Optional[List[str]] = None):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators
        )

    def __call__(self, text: str, metadata: Optional[dict] = None) -> List[dict]:
        chunks = self.text_splitter.split_text(text)
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {"content": chunk, "chunk_order": i}
            if metadata:
                doc.update(metadata)
            documents.append(doc)
        return documents
