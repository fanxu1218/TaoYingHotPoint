from typing import Any, Dict, List
from urllib.parse import quote

from collector.models import HotItem
from collector.providers.base import Provider


class WeiboProvider(Provider):
    source = "weibo"
    url = "https://weibo.com/ajax/side/hotSearch"

    @staticmethod
    def parse(payload: Dict[str, Any], limit: int = 100) -> List[HotItem]:
        realtime = payload.get("data", {}).get("realtime", [])
        items: List[HotItem] = []
        for row in realtime:
            if len(items) >= limit:
                break
            if row.get("is_ad"):
                continue
            title = str(row.get("word") or row.get("note") or "").strip()
            if not title:
                continue
            scheme = str(row.get("scheme") or "")
            url = scheme if scheme.startswith("http") else f"https://s.weibo.com/weibo?q={quote(title)}"
            score = row.get("num")
            items.append(HotItem(
                source="weibo",
                external_id=str(row.get("word_scheme") or title),
                title=title,
                url=url,
                rank=len(items) + 1,
                hot_score=int(score) if isinstance(score, (int, float)) else None,
                summary=str(row.get("label_name") or "") or None,
            ).normalized())
        return items

    def fetch(self) -> List[HotItem]:
        payload = self.client.get_json(self.url, headers={"Referer": "https://weibo.com/"})
        return self.parse(payload, self.limit)
