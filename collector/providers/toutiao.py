from typing import Any, Dict, List

from collector.models import HotItem
from collector.providers.base import Provider


class ToutiaoProvider(Provider):
    source = "toutiao"
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"

    @staticmethod
    def parse(payload: Dict[str, Any], limit: int = 100) -> List[HotItem]:
        rows = payload.get("data", [])
        items: List[HotItem] = []
        for row in rows[:limit]:
            title = str(row.get("Title") or row.get("title") or "").strip()
            url = str(row.get("Url") or row.get("url") or "").strip()
            if not title or not url:
                continue
            score = row.get("HotValue") if row.get("HotValue") is not None else row.get("hot_value")
            external_id = str(row.get("ClusterIdStr") or row.get("ClusterId") or title)
            items.append(HotItem(
                source="toutiao",
                external_id=external_id,
                title=title,
                url=url,
                rank=len(items) + 1,
                hot_score=int(score) if isinstance(score, (int, float)) else None,
                summary=str(row.get("Label") or row.get("label") or "") or None,
                cover_url=str(row.get("Image") or row.get("image") or "") or None,
            ).normalized())
        return items

    def fetch(self) -> List[HotItem]:
        payload = self.client.get_json(self.url, headers={"Referer": "https://www.toutiao.com/"})
        return self.parse(payload, self.limit)
