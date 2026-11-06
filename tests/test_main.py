import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from collector.main import main
from collector.models import HotItem


def provider(source: str, failed: bool = False) -> Mock:
    result = Mock(source=source)
    if failed:
        result.fetch.side_effect = RuntimeError("测试接口不可用")
    else:
        result.fetch.return_value = [HotItem(source=source, title="测试热点", url="https://example.com", rank=1)]
    return result


class CollectionFailureTests(unittest.TestCase):
    def collect(self, providers, arguments, database_url="postgresql://test"):
        output = io.StringIO()
        with patch("sys.argv", ["collector", *arguments]), \
             patch.dict("os.environ", {"DATABASE_URL": database_url}), \
             patch("collector.main.build_providers", return_value=providers), \
             patch("collector.main.PostgresStorage") as storage_class, \
             self.assertLogs("collector", level="INFO"), redirect_stdout(output):
            storage = storage_class.return_value
            storage.save_items.return_value = 1
            storage.get_database_usage.return_value = {"status": "ok"}
            code = main()
        return code, json.loads(output.getvalue()), storage_class

    def test_required_failure_does_not_stop_other_writes(self):
        providers = [provider("baidu", failed=True), provider("weibo"), provider("tencent")]
        code, report, storage_class = self.collect(providers, ["--strict"])
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "partial")
        self.assertEqual(storage_class.return_value.save_items.call_count, 2)
        self.assertEqual(report["sources"]["tencent"]["status"], "success")
        recorded = storage_class.return_value.record_run.call_args.args[2]
        self.assertEqual(recorded, report["sources"])

    def test_optional_failure_stays_visible_without_failing_required_sources(self):
        code, report, _ = self.collect(
            [provider("baidu"), provider("xiaohongshu", failed=True), provider("tencent")],
            ["--strict", "--optional-source", "xiaohongshu"],
        )
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "partial")
        self.assertFalse(report["sources"]["xiaohongshu"]["required"])
        self.assertEqual(report["sources"]["xiaohongshu"]["status"], "failed")

    def test_no_success_is_a_failure_even_for_optional_sources(self):
        code, report, _ = self.collect(
            [provider("xiaohongshu", failed=True)], ["--strict", "--optional-source", "xiaohongshu"],
        )
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "failed")

    def test_recovered_optional_source_is_collected_normally(self):
        code, report, storage_class = self.collect(
            [provider("baidu"), provider("xiaohongshu")], ["--strict", "--optional-source", "xiaohongshu"],
        )
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "success")
        self.assertEqual(storage_class.return_value.save_items.call_count, 2)

    def test_dry_run_never_opens_storage_with_database_configured(self):
        code, report, storage_class = self.collect([provider("baidu")], ["--dry-run", "--strict"])
        self.assertEqual(code, 0)
        storage_class.assert_not_called()
        self.assertIsNone(report["database"])
