import io
from pathlib import Path
from .base import BaseReader

SUPPORTED = {".txt", ".md", ".pdf", ".docx"}


class LocalReader(BaseReader):
    def __init__(self, path: str, allowed_roles: list[str] = None):
        self.path = Path(path)
        self.allowed_roles = allowed_roles or ["all"]

    def load(self) -> list[dict]:
        files = [self.path] if self.path.is_file() else list(self.path.rglob("*"))
        documents = []
        for file in files:
            if file.suffix.lower() not in SUPPORTED:
                continue
            content = self._extract(file)
            if content:
                documents.append({
                    "content": content,
                    "title": file.stem,
                    "source": f"local:{file}",
                    "file_type": file.suffix.lstrip("."),
                    "allowed_roles": self.allowed_roles,
                })
        return documents

    def _extract(self, file: Path) -> str:
        ext = file.suffix.lower()
        if ext in {".txt", ".md"}:
            return file.read_text(encoding="utf-8", errors="ignore")
        if ext == ".pdf":
            import fitz
            doc = fitz.open(str(file))
            text = "".join(page.get_text() + "\n" for page in doc)
            doc.close()
            return text
        if ext == ".docx":
            from docx import Document
            return "\n".join(p.text for p in Document(str(file)).paragraphs if p.text)
        return ""
