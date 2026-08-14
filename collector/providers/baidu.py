import html
import json
import re
from typing import Any, Dict, List

from collector.models import HotItem
from collector.providers.base import Provider


class BaiduProvider(Provider):
    source = "baidu"
    url = "https://top.baidu.com/board?tab=realtime"

    @staticmethod
    def parse(page: str, limit: int = 100) -> List[HotItem]:
        match = re.search(r"<!--s-data:(.*?)-->", page, re.DOTALL)
        if not match:
            raise ValueError("百度热搜页面中未找到榜单数据")
        payload: Dict[str, Any] = json.loads(html.unescape(match.group(1)))
        cards = payload.get("data", {}).get("cards", [])
        content = next((card.get("content", []) for card in cards if card.get("component") == "hotList"), [])
        items: List[HotItem] = []
        for index, row in enumerate(content[:limit], start=1):
            title = str(row.get("word") or row.get("query") or "").strip()
            url = str(row.get("url") or row.get("rawUrl") or "").strip()
            if not title or not url:
                continue
            score_text = str(row.get("hotScore") or "").replace(",", "")
            items.append(HotItem(
                source="baidu",
                external_id=title,
                title=title,
                url=url,
                rank=index,
                hot_score=int(score_text) if score_text.isdigit() else None,
                summary=str(row.get("desc") or "") or None,
                cover_url=str(row.get("img") or "") or None,
            ).normalized())
        return items

    def fetch(self) -> List[HotItem]:
        return self.parse(self.client.get(self.url).text, self.limit)
