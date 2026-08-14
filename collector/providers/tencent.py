from typing import Any, Dict, List

from collector.models import HotItem
from collector.providers.base import Provider


class TencentProvider(Provider):
    source = "tencent"
    url = (
        "https://r.inews.qq.com/gw/event/pc_hot_ranking_list"
        "?ids_hash=&offset=0&page_size=100&appver=15.5_qqnews_7.1.60&rank_id=hot"
    )

    @staticmethod
    def parse(payload: Dict[str, Any], limit: int = 100) -> List[HotItem]:
        groups = payload.get("idlist", [])
        rows = groups[0].get("newslist", []) if groups else []
        items: List[HotItem] = []
        for row in rows:
            event = row.get("hotEvent") or {}
            ranking = event.get("ranking") or row.get("ranking")
            if not ranking:
                continue
            title = str(event.get("title") or row.get("title") or "").strip()
            url = str(row.get("url") or row.get("surl") or "").strip()
            if not title or not url:
                continue
            score = event.get("hotScore")
            cover = row.get("fimgUrl")
            if not isinstance(cover, str) or not cover:
                big_images = row.get("bigImage")
                cover = big_images[0] if isinstance(big_images, list) and big_images else None
            items.append(HotItem(
                source="tencent",
                external_id=str(event.get("id") or row.get("id") or title),
                title=title,
                url=url,
                rank=int(ranking),
                hot_score=int(score) if isinstance(score, (int, float)) else None,
                summary=str(row.get("abstract") or row.get("nlpAbstract") or "") or None,
                cover_url=cover if isinstance(cover, str) else None,
            ).normalized())
            if len(items) >= limit:
                break
        return sorted(items, key=lambda item: item.rank)

    def fetch(self) -> List[HotItem]:
        payload = self.client.get_json(self.url, headers={"Referer": "https://news.qq.com/"})
        return self.parse(payload, self.limit)
