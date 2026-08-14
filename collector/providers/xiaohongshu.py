from typing import Any, Dict, List
from urllib.parse import quote

from collector.models import HotItem
from collector.providers.base import Provider


class XiaohongshuProvider(Provider):
    source = "xiaohongshu"
    urls = (
        "https://edith.xiaohongshu.com/api/sns/web/v1/search/hot_list",
        "https://edith.xiaohongshu.com/api/sns/v1/search/hot_list",
    )

    @staticmethod
    def parse(payload: Dict[str, Any], limit: int = 100) -> List[HotItem]:
        data = payload.get("data", {})
        rows = data.get("items") or data.get("queries") or data.get("hot_list") or []
        items: List[HotItem] = []
        for row in rows[:limit]:
            title = str(row.get("title") or row.get("search_word") or row.get("word") or "").strip()
            if not title:
                continue
            score = row.get("score") or row.get("hot_score") or row.get("heat")
            items.append(HotItem(
                source="xiaohongshu",
                external_id=str(row.get("word_request_id") or row.get("query_id") or title),
                title=title,
                url=f"https://www.xiaohongshu.com/search_result?keyword={quote(title)}",
                rank=len(items) + 1,
                hot_score=int(score) if isinstance(score, (int, float)) else None,
                summary=str(row.get("type") or "") or None,
                cover_url=str(row.get("icon") or "") or None,
            ).normalized())
        return items

    def fetch(self) -> List[HotItem]:
        errors: List[str] = []
        for url in self.urls:
            try:
                payload = self.client.get_json(url, headers={"Referer": "https://www.xiaohongshu.com/"})
                items = self.parse(payload, self.limit)
                if items:
                    return items
                errors.append(f"{url}: 榜单为空")
            except Exception as error:  # 单个公开入口失效时尝试下一个官方入口
                errors.append(f"{url}: {error}")
        raise RuntimeError("；".join(errors))
