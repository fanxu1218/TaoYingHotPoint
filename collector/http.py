import logging
import time
from typing import Any, Dict, Optional

import requests


LOGGER = logging.getLogger(__name__)


class HttpClient:
    def __init__(self, timeout: int = 20, retries: int = 2) -> None:
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
        })

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as error:
                last_error = error
                if attempt < self.retries:
                    delay = 1.5 ** attempt
                    LOGGER.warning("请求失败，%.1f 秒后重试：%s", delay, url)
                    time.sleep(delay)
        assert last_error is not None
        raise last_error

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        payload = self.get(url, headers=headers).json()
        if not isinstance(payload, dict):
            raise ValueError(f"接口未返回 JSON 对象：{url}")
        return payload
