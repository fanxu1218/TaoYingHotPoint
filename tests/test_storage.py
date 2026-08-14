import unittest

from collector.storage import build_database_usage


class DatabaseUsageTests(unittest.TestCase):
    def test_usage_is_ok_below_warning_threshold(self) -> None:
        usage = build_database_usage(399 * 1024 * 1024)
        self.assertEqual(usage["status"], "ok")
        self.assertEqual(usage["size_mb"], 399.0)

    def test_usage_warns_at_400_mb(self) -> None:
        usage = build_database_usage(400 * 1024 * 1024)
        self.assertEqual(usage["status"], "warning")
        self.assertEqual(usage["usage_percent"], 80.0)

    def test_usage_is_critical_at_free_limit(self) -> None:
        usage = build_database_usage(500 * 1024 * 1024)
        self.assertEqual(usage["status"], "critical")
        self.assertEqual(usage["usage_percent"], 100.0)

    def test_negative_size_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_database_usage(-1)


if __name__ == "__main__":
    unittest.main()
