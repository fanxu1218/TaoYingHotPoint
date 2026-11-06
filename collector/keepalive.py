"""仓库连续 30 天无提交时准备一次可审计的定时任务维护记录。"""

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


HEARTBEAT_PATH = Path(".github/schedule-heartbeat.json")


def prepare_heartbeat(repo: Path, now: Optional[datetime] = None) -> bool:
    now = now or datetime.now(timezone.utc)
    timestamp = subprocess.check_output(["git", "log", "-1", "--format=%ct"], cwd=repo, text=True).strip()
    last_commit = datetime.fromtimestamp(int(timestamp), timezone.utc)
    if now - last_commit < timedelta(days=30):
        print("仓库最近 30 天内有提交，无需更新定时任务维护记录。")
        return False

    run_id = os.getenv("GITHUB_RUN_ID")
    repository = os.getenv("GITHUB_REPOSITORY")
    record = {
        "checked_at": now.isoformat(),
        "reason": "Prevent GitHub scheduled workflow inactivity after 60 days",
        "workflow_run": f"https://github.com/{repository}/actions/runs/{run_id}" if repository and run_id else None,
    }
    path = repo / HEARTBEAT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已更新定时任务维护记录：{HEARTBEAT_PATH}")
    return True


if __name__ == "__main__":
    prepare_heartbeat(Path.cwd())
