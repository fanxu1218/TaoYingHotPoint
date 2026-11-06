import io
import unittest
from contextlib import redirect_stdout

from collector.report import render_report


class CollectionReportTests(unittest.TestCase):
    def test_optional_failure_warns_and_required_failure_errors(self):
        output = io.StringIO()
        report = {"sources": {
            "baidu": {"status": "failed", "count": 0, "required": True, "error": "网络异常"},
            "weibo": {"status": "success", "count": 50, "required": True},
            "xiaohongshu": {
                "status": "failed", "count": 0, "required": False,
                "error": "HTTP 406\n::error::不应成为独立注解 100%",
            },
        }, "database": {"status": "ok", "size_mb": 27.73, "limit_mb": 500, "usage_percent": 5.55, "warning_mb": 400}}
        with redirect_stdout(output):
            summary = render_report(report)
        annotations = output.getvalue().splitlines()
        self.assertEqual(len(annotations), 2)
        self.assertTrue(annotations[0].startswith("::error title=百度"))
        self.assertTrue(annotations[1].startswith("::warning title=小红书"))
        self.assertIn("%0A", annotations[1])
        self.assertIn("100%25", annotations[1])
        self.assertIn("部分成功", summary)
        self.assertIn("| 小红书 | 可选 | 暂不可用 | 0 |", summary)
        self.assertIn("27.73 MB", summary)
