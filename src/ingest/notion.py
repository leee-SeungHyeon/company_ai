import os
from notion_client import Client
from .base import BaseReader


class NotionReader(BaseReader):
    def __init__(self, token: str = None, database_id: str = None, page_ids: list[str] = None):
        self.client = Client(auth=token or os.getenv("NOTION_TOKEN"))
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        raw = os.getenv("NOTION_PAGE_IDS", "")
        self.page_ids = page_ids or [p.strip() for p in raw.split(",") if p.strip()]

    def load(self) -> list[dict]:
        documents = []
        if self.database_id:
            for page in self._fetch_database_pages():
                documents.append(self._page_to_doc(page))
        for page_id in self.page_ids:
            page = self.client.pages.retrieve(page_id=page_id)
            documents.append(self._page_to_doc(page))
        return documents

    def _page_to_doc(self, page: dict) -> dict:
        page_id = page["id"]
        return {
            "content": self._extract_content(page_id),
            "title": self._get_title(page),
            "source": f"notion:{page_id}",
            "file_type": "notion",
        }

    def _fetch_database_pages(self) -> list:
        pages, cursor = [], None
        while True:
            kwargs = {"database_id": self.database_id}
            if cursor:
                kwargs["start_cursor"] = cursor
            response = self.client.databases.query(**kwargs)
            pages.extend(response["results"])
            if not response["has_more"]:
                break
            cursor = response["next_cursor"]
        return pages

    def _extract_content(self, page_id: str) -> str:
        blocks = self._fetch_blocks(page_id)
        return "\n".join(self._block_to_text(b) for b in blocks if self._block_to_text(b))

    def _fetch_blocks(self, block_id: str) -> list:
        blocks, cursor = [], None
        while True:
            kwargs = {"block_id": block_id}
            if cursor:
                kwargs["start_cursor"] = cursor
            response = self.client.blocks.children.list(**kwargs)
            blocks.extend(response["results"])
            if not response["has_more"]:
                break
            cursor = response["next_cursor"]
        return blocks

    def _block_to_text(self, block: dict) -> str:
        t = block["type"]
        text_types = {"paragraph", "heading_1", "heading_2", "heading_3",
                      "bulleted_list_item", "numbered_list_item", "quote", "callout"}
        if t in text_types:
            return "".join(rt["plain_text"] for rt in block[t].get("rich_text", []))
        if t == "code":
            code = "".join(rt["plain_text"] for rt in block["code"].get("rich_text", []))
            return f"```\n{code}\n```"
        return ""

    def _get_title(self, page: dict) -> str:
        for prop in page.get("properties", {}).values():
            if prop["type"] == "title" and prop["title"]:
                return prop["title"][0]["plain_text"]
        return "Untitled"
