import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from collector.keepalive import HEARTBEAT_PATH, prepare_heartbeat


class ScheduleMaintenanceTests(unittest.TestCase):
    def test_only_prepares_a_record_after_30_days_and_preserves_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            initial = datetime(2026, 9, 1, tzinfo=timezone.utc)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

            def commit(moment):
                env = dict(os.environ, GIT_AUTHOR_DATE=moment.isoformat(), GIT_COMMITTER_DATE=moment.isoformat())
                subprocess.run([
                    "git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
                    "commit", "--allow-empty", "-qm", "test activity",
                ], cwd=repo, env=env, check=True)

            commit(initial)
            personal_file = repo / "notes.txt"
            personal_file.write_text("保留未提交内容", encoding="utf-8")
            self.assertFalse(prepare_heartbeat(repo, initial + timedelta(days=29)))
            self.assertFalse((repo / HEARTBEAT_PATH).exists())
            refresh_at = initial + timedelta(days=30)
            self.assertTrue(prepare_heartbeat(repo, refresh_at))
            record_path = repo / HEARTBEAT_PATH
            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual(record["checked_at"], refresh_at.isoformat())
            subprocess.run(["git", "add", "--", str(HEARTBEAT_PATH)], cwd=repo, check=True)
            commit(refresh_at)
            self.assertFalse(prepare_heartbeat(repo, refresh_at + timedelta(days=1)))
            self.assertEqual(json.loads(record_path.read_text(encoding="utf-8")), record)
            self.assertEqual(personal_file.read_text(encoding="utf-8"), "保留未提交内容")
