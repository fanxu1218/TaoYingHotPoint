from dataclasses import dataclass
from hashlib import sha256
from typing import Optional


@dataclass(frozen=True)
class HotItem:
    source: str
    title: str
    url: str
    rank: int
    external_id: str = ""
    hot_score: Optional[int] = None
    summary: Optional[str] = None
    cover_url: Optional[str] = None

    def normalized(self) -> "HotItem":
        title = " ".join(self.title.split()).strip()[:500]
        url = self.url.strip()[:2000]
        summary = " ".join((self.summary or "").split()).strip()[:1000] or None
        external_id = self.external_id.strip()[:300]
        if not external_id:
            external_id = sha256(f"{self.source}|{url}|{title}".encode("utf-8")).hexdigest()
        return HotItem(
            source=self.source,
            external_id=external_id,
            title=title,
            url=url,
            rank=max(1, self.rank),
            hot_score=max(0, self.hot_score) if self.hot_score is not None else None,
            summary=summary,
            cover_url=(self.cover_url or "").strip()[:2000] or None,
        )
