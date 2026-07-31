"""Hacker News RSS 抓取"""

import re
from typing import Optional
from urllib.parse import urlparse

import requests

from src.crawler.base import BaseCrawler
from .models import Story

HACKERNEWS_RSS = "https://hnrss.org/frontpage"


class HackerNewsCrawler(BaseCrawler):
    """通过 hnrss.org RSS feed 抓取 Hacker News 热门文章"""

    def __init__(self, proxy: Optional[str] = None):
        self._proxy = proxy

    @property
    def name(self) -> str:
        return "Hacker News"

    def crawl(self) -> list[Story]:
        """抓取 RSS 并解析为 Story 列表"""
        url = HACKERNEWS_RSS
        print(f"[Crawler:HN] 正在抓取: {url}")

        proxies = None
        if self._proxy:
            proxies = {"http": self._proxy, "https": self._proxy}

        resp = requests.get(url, timeout=15, proxies=proxies)
        resp.raise_for_status()

        # 用简单的 XML 解析（避免额外依赖 feedparser）
        stories = []
        items = re.findall(r"<item>(.*?)</item>", resp.text, re.DOTALL)

        for item_xml in items:
            title = _extract_cdata(item_xml, "title")
            link = _extract_text(item_xml, "link")
            description = _extract_cdata(item_xml, "description")
            dc_creator = _extract_text(item_xml, "dc:creator")
            comments = _extract_text(item_xml, "comments")

            # 从 description 中提取 points
            points_match = re.search(r"Points:\s*(\d+)", description)
            points = points_match.group(1) if points_match else ""

            # 从 link 中提取评论区链接（hnrss 的 link 就是原文链接）
            # comments 字段是 HN 评论区
            source = ""
            if link and "github.com" not in link:
                parsed = urlparse(link)
                source = parsed.netloc

            stories.append(Story(
                title=title,
                url=link,
                points=points,
                author=dc_creator,
                comments=re.search(r"Comments:\s*(\d+)", description).group(1)
                if re.search(r"Comments:\s*(\d+)", description)
                else "",
                comments_url=comments,
                source=source,
            ))

        print(f"[Crawler:HN] 解析完成，共 {len(stories)} 篇文章")
        return stories


def _extract_text(xml: str, tag: str) -> str:
    """从 XML 片段中提取指定标签的文本内容"""
    match = re.search(f"<{tag}>(.*?)</{tag}>", xml)
    return match.group(1).strip() if match else ""


def _extract_cdata(xml: str, tag: str) -> str:
    """从 XML 片段中提取 CDATA 内容"""
    match = re.search(f"<{tag}><!\\[CDATA\\[(.*?)\\]\\]></{tag}>", xml, re.DOTALL)
    return match.group(1).strip() if match else ""
