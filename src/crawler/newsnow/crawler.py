"""NewsNow 聚合热榜抓取 — 支持微博/知乎/抖音/掘金/ProductHunt 等几十个平台"""

from typing import Optional

import requests

from src.crawler.base import BaseCrawler
from .models import HotItem

NEWSNOW_API = "https://newsnow.busiyi.world/api/s"

# 平台 ID → 显示名映射
PLATFORM_NAMES: dict[str, str] = {
    "zhihu": "知乎",
    "weibo": "微博",
    "douyin": "抖音",
    "baidu": "百度",
    "toutiao": "今日头条",
    "bilibili-hot-search": "B站",
    "wallstreetcn-hot": "华尔街见闻",
    "thepaper": "澎湃新闻",
    "cls-hot": "财联社",
    "ifeng": "凤凰网",
    "tieba": "贴吧",
    "juejin": "稀土掘金",
    "nowcoder": "牛客",
    "producthunt": "Product Hunt",
    "github-trending-today": "GitHub",
    "hacker-news": "Hacker News",
}


class NewsNowCrawler(BaseCrawler):
    """通过 NewsNow 聚合 API 抓取各平台热榜"""

    def __init__(
        self,
        platform: str,
        proxy: Optional[str] = None,
    ):
        self._platform = platform
        self._proxy = proxy

    @property
    def name(self) -> str:
        return PLATFORM_NAMES.get(self._platform, self._platform)

    def crawl(self) -> list[HotItem]:
        url = f"{NEWSNOW_API}?id={self._platform}&latest"
        print(f"[Crawler:NewsNow] 正在抓取: {url}")

        proxies = None
        if self._proxy:
            proxies = {"http": self._proxy, "https": self._proxy}

        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; github-trends-pusher)",
                "Accept": "application/json",
            },
            timeout=15,
            proxies=proxies,
        )
        resp.raise_for_status()
        data = resp.json()

        platform_name = PLATFORM_NAMES.get(self._platform, self._platform)
        items = []

        for i, item in enumerate(data.get("items", []), 1):
            title = item.get("title", "")
            url = item.get("url", "")
            extra = item.get("extra", {})

            # 热度字段各平台格式不同，统一提取
            heat = extra.get("heat") or extra.get("info") or ""

            items.append(HotItem(
                title=title,
                url=url,
                rank=i,
                heat=str(heat) if heat else "",
                platform=self._platform,
                platform_name=platform_name,
            ))

        status = data.get("status", "unknown")
        print(f"[Crawler:NewsNow] 抓取完成 [{platform_name}]: {status}, {len(items)} 条")
        return items
