import io
import os
import requests
import msal
from .base import BaseReader

GRAPH_URL = "https://graph.microsoft.com/v1.0"
SUPPORTED = {".pdf", ".txt", ".md", ".docx"}


class OneDriveReader(BaseReader):
    def __init__(self, client_id: str = None, client_secret: str = None, tenant_id: str = None, folder_path: str = None, allowed_roles: list[str] = None):
        self.client_id = client_id or os.getenv("ONEDRIVE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("ONEDRIVE_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("ONEDRIVE_TENANT_ID")
        self.folder_path = folder_path or os.getenv("ONEDRIVE_FOLDER_PATH", "/")
        self.allowed_roles = allowed_roles or ["all"]

    def load(self) -> list[dict]:
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        documents = []
        for file in self._list_files(headers):
            ext = "." + file["name"].rsplit(".", 1)[-1].lower()
            if ext not in SUPPORTED:
                continue
            content = self._extract(file, headers, ext)
            if content:
                documents.append({
                    "content": content,
                    "title": file["name"],
                    "source": f"onedrive:{file['id']}",
                    "file_type": ext.lstrip("."),
                    "allowed_roles": self.allowed_roles,
                })
        return documents

    def _get_token(self) -> str:
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in result:
            raise RuntimeError(f"OneDrive 토큰 획득 실패: {result.get('error_description')}")
        return result["access_token"]

    def _list_files(self, headers: dict) -> list:
        url = (f"{GRAPH_URL}/me/drive/root/children" if self.folder_path == "/"
               else f"{GRAPH_URL}/me/drive/root:/{requests.utils.quote(self.folder_path)}:/children")
        files = []
        while url:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
            files.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
        return files

    def _extract(self, file: dict, headers: dict, ext: str) -> str:
        url = file.get("@microsoft.graph.downloadUrl")
        if not url:
            return ""
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        if ext in {".txt", ".md"}:
            return r.text
        if ext == ".pdf":
            import fitz
            doc = fitz.open(stream=io.BytesIO(r.content), filetype="pdf")
            text = "".join(page.get_text() + "\n" for page in doc)
            doc.close()
            return text
        if ext == ".docx":
            from docx import Document
            return "\n".join(p.text for p in Document(io.BytesIO(r.content)).paragraphs if p.text)
        return ""
