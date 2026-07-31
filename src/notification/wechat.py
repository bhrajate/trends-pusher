"""微信推送发送器（基于 Server酱）"""

from typing import Any, Optional

import requests

from src.crawler.base import Repo

from .base import BaseSender
from .formatter import format_trending

SERVERCHAN_URL = "https://sctapi.ftqq.com"


class WeChatSender(BaseSender):
    """通过 Server酱 推送到微信"""

    def __init__(self, sendkey: str, proxy: Optional[str] = None):
        self._sendkey = sendkey
        self._proxy = proxy

    @property
    def channel_name(self) -> str:
        return "微信（Server酱）"

    @classmethod
    def validate_config(cls, config: dict) -> bool:
        sendkey = config.get("sendkey", "")
        return bool(sendkey and sendkey.strip())

    def send(
        self,
        repos: list[Repo],
        display_cfg: dict[str, Any],
        since: str = "daily",
    ) -> bool:
        """发送消息到微信"""
        content = format_trending(
            repos,
            channel="wechat",
            max_items=display_cfg.get("max_items", 25),
            show_language_color=display_cfg.get("show_language_color", True),
            show_description=display_cfg.get("show_description", True),
            since=since,
        )

        url = f"{SERVERCHAN_URL}/{self._sendkey}.send"
        lines = content.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else "GitHub Trending"

        payload = {"title": title, "desp": content}

        proxies = None
        if self._proxy:
            proxies = {"http": self._proxy, "https": self._proxy}

        try:
            resp = requests.post(url, data=payload, timeout=15, proxies=proxies)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 0:
                print(f"[微信] 发送成功")
                return True
            else:
                print(f"[微信] 发送失败: {result.get('message', '未知错误')}")
                return False
        except requests.RequestException as e:
            print(f"[微信] 请求失败: {e}")
            return False
