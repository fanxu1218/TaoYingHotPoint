import json
from datetime import date, datetime, timezone
from typing import Dict, Iterable, Optional

import psycopg

from collector.models import HotItem


class PostgresStorage:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def save_items(self, items: Iterable[HotItem], captured_date: date) -> int:
        saved = 0
        captured_at = datetime.now(timezone.utc)
        with psycopg.connect(self.database_url, prepare_threshold=None) as connection:
            with connection.cursor() as cursor:
                for item in items:
                    cursor.execute(
                        """
                        insert into public.hot_topics (
                          source, external_id, title, url, summary, cover_url, first_seen_at, last_seen_at
                        ) values (%s, %s, %s, %s, %s, %s, %s, %s)
                        on conflict (source, external_id) do update set
                          title = excluded.title,
                          url = excluded.url,
                          summary = excluded.summary,
                          cover_url = excluded.cover_url,
                          last_seen_at = excluded.last_seen_at
                        returning id
                        """,
                        (
                            item.source, item.external_id, item.title, item.url, item.summary,
                            item.cover_url, captured_at, captured_at,
                        ),
                    )
                    topic_id = cursor.fetchone()[0]
                    cursor.execute(
                        """
                        insert into public.hot_topic_snapshots (
                          topic_id, captured_date, captured_at, rank, hot_score
                        ) values (%s, %s, %s, %s, %s)
                        on conflict (topic_id, captured_date) do update set
                          captured_at = excluded.captured_at,
                          rank = excluded.rank,
                          hot_score = excluded.hot_score
                        """,
                        (topic_id, captured_date, captured_at, item.rank, item.hot_score),
                    )
                    saved += 1
        return saved

    def record_run(
        self,
        started_at: datetime,
        finished_at: datetime,
        statuses: Dict[str, Dict[str, object]],
        error: Optional[str] = None,
    ) -> None:
        total = sum(int(status.get("count", 0)) for status in statuses.values())
        succeeded = sum(1 for status in statuses.values() if status.get("status") == "success")
        state = "success" if succeeded == len(statuses) else "partial" if succeeded else "failed"
        with psycopg.connect(self.database_url, prepare_threshold=None) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into public.collection_runs (
                      started_at, finished_at, status, item_count, source_statuses, error_message
                    ) values (%s, %s, %s, %s, %s::jsonb, %s)
                    """,
                    (started_at, finished_at, state, total, json.dumps(statuses, ensure_ascii=False), error),
                )
