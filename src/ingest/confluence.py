import os
from atlassian import Confluence
from bs4 import BeautifulSoup
from .base import BaseReader


class ConfluenceReader(BaseReader):
    def __init__(self, url: str = None, username: str = None, api_token: str = None, space_key: str = None, allowed_roles: list[str] = None):
        self.confluence = Confluence(
            url=url or os.getenv("CONFLUENCE_URL"),
            username=username or os.getenv("CONFLUENCE_USERNAME"),
            password=api_token or os.getenv("CONFLUENCE_API_TOKEN"),
            cloud=True,
        )
        self.space_key = space_key or os.getenv("CONFLUENCE_SPACE_KEY")
        self.allowed_roles = allowed_roles or ["all"]

    def load(self) -> list[dict]:
        return [self._page_to_doc(page) for page in self._fetch_all_pages()]

    def _fetch_all_pages(self) -> list:
        pages, start, limit = [], 0, 50
        while True:
            batch = self.confluence.get_all_pages_from_space(
                space=self.space_key, start=start, limit=limit, expand="body.storage"
            )
            if not batch:
                break
            pages.extend(batch)
            if len(batch) < limit:
                break
            start += limit
        return pages

    def _page_to_doc(self, page: dict) -> dict:
        html = page.get("body", {}).get("storage", {}).get("value", "")
        content = BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)
        return {
            "content": content,
            "title": page["title"],
            "source": f"confluence:{page['id']}",
            "file_type": "confluence",
            "allowed_roles": self.allowed_roles,
        }
