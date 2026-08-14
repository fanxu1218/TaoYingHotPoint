import json
import unittest

from collector.providers.baidu import BaiduProvider
from collector.providers.tencent import TencentProvider
from collector.providers.toutiao import ToutiaoProvider
from collector.providers.weibo import WeiboProvider
from collector.providers.xiaohongshu import XiaohongshuProvider


class ProviderParserTests(unittest.TestCase):
    def test_baidu_parser(self) -> None:
        data = {"data": {"cards": [{"component": "hotList", "content": [{
            "word": "测试热点", "url": "https://example.com/baidu", "hotScore": "12000", "desc": "摘要"
        }]}]}}
        page = f"<div><!--s-data:{json.dumps(data, ensure_ascii=False)}--></div>"
        items = BaiduProvider.parse(page)
        self.assertEqual(items[0].title, "测试热点")
        self.assertEqual(items[0].hot_score, 12000)

    def test_weibo_filters_ads(self) -> None:
        payload = {"data": {"realtime": [
            {"word": "广告", "is_ad": 1, "num": 999},
            {"word": "真实热点", "num": 88},
        ]}}
        items = WeiboProvider.parse(payload)
        self.assertEqual([item.title for item in items], ["真实热点"])
        self.assertEqual(items[0].rank, 1)

    def test_toutiao_parser(self) -> None:
        payload = {"data": [{"Title": "头条热点", "Url": "https://example.com/toutiao", "HotValue": 100, "ClusterIdStr": "abc"}]}
        items = ToutiaoProvider.parse(payload)
        self.assertEqual(items[0].external_id, "abc")

    def test_xiaohongshu_parser(self) -> None:
        payload = {"data": {"items": [{"title": "生活趋势", "score": 99, "word_request_id": "xhs-1"}]}}
        items = XiaohongshuProvider.parse(payload)
        self.assertIn("keyword=", items[0].url)

    def test_tencent_skips_intro_row(self) -> None:
        payload = {"idlist": [{"newslist": [
            {"id": "intro", "title": "榜单说明"},
            {"id": "news-1", "url": "https://example.com/tencent", "abstract": "摘要", "hotEvent": {"id": "event-1", "ranking": 1, "title": "腾讯热点", "hotScore": 200}},
        ]}]}
        items = TencentProvider.parse(payload)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "腾讯热点")


if __name__ == "__main__":
    unittest.main()
