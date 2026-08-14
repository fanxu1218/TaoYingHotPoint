import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List
from zoneinfo import ZoneInfo

from collector.http import HttpClient
from collector.providers import BaiduProvider, TencentProvider, ToutiaoProvider, WeiboProvider, XiaohongshuProvider
from collector.providers.base import Provider
from collector.storage import PostgresStorage


LOGGER = logging.getLogger("collector")


def build_providers(client: HttpClient, limit: int) -> List[Provider]:
    return [
        BaiduProvider(client, limit),
        WeiboProvider(client, limit),
        ToutiaoProvider(client, limit),
        XiaohongshuProvider(client, limit),
        TencentProvider(client, limit),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="采集公开平台热点榜")
    parser.add_argument("--limit", type=int, default=100, help="每个平台最多采集条数")
    parser.add_argument("--dry-run", action="store_true", help="只采集和打印状态，不写数据库")
    parser.add_argument("--strict", action="store_true", help="任一平台失败时返回失败状态")
    args = parser.parse_args()

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
    database_url = os.getenv("DATABASE_URL", "")
    if not args.dry_run and not database_url:
        LOGGER.error("缺少 DATABASE_URL")
        return 2

    started_at = datetime.now(timezone.utc)
    client = HttpClient()
    storage = PostgresStorage(database_url) if database_url else None
    statuses: Dict[str, Dict[str, object]] = {}

    for provider in build_providers(client, max(1, min(args.limit, 100))):
        try:
            items = provider.fetch()
            if not items:
                raise ValueError("榜单返回 0 条数据")
            saved = len(items)
            if storage:
                saved = storage.save_items(items, datetime.now(ZoneInfo("Asia/Shanghai")).date())
            statuses[provider.source] = {"status": "success", "count": saved}
            LOGGER.info("%s：采集 %d 条", provider.source, saved)
        except Exception as error:
            statuses[provider.source] = {"status": "failed", "count": 0, "error": str(error)[:500]}
            LOGGER.exception("%s：采集失败", provider.source)

    finished_at = datetime.now(timezone.utc)
    if storage:
        storage.record_run(started_at, finished_at, statuses)

    print(json.dumps(statuses, ensure_ascii=False, indent=2))
    succeeded = sum(1 for status in statuses.values() if status["status"] == "success")
    if succeeded == 0 or (args.strict and succeeded != len(statuses)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
