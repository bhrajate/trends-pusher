"""GitHub Trending 页面抓取实现"""

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseCrawler, Repo

GITHUB_TRENDING_URL = "https://github.com/trending"


class GitHubTrendingCrawler(BaseCrawler):
    """从 GitHub Trending 页面抓取热门仓库"""

    def __init__(
        self,
        since: str = "daily",
        language: str = "",
        spoken_language: str = "",
        proxy: Optional[str] = None,
    ):
        self._since = since
        self._language = language
        self._spoken_language = spoken_language
        self._proxy = proxy

    @property
    def name(self) -> str:
        return "GitHub Trending"

    def _build_url(self) -> str:
        """构建请求 URL"""
        if self._language:
            url = f"{GITHUB_TRENDING_URL}/{self._language}"
        else:
            url = GITHUB_TRENDING_URL

        params = []
        if self._since and self._since != "daily":
            params.append(f"since={self._since}")
        if self._spoken_language:
            params.append(f"spoken_language_code={self._spoken_language}")

        if params:
            url += "?" + "&".join(params)

        return url

    def crawl(self) -> list[Repo]:
        """抓取 GitHub Trending 并解析为 Repo 列表"""
        url = self._build_url()
        print(f"[Crawler] 正在抓取: {url}")

        proxies = None
        if self._proxy:
            proxies = {"http": self._proxy, "https": self._proxy}

        resp = requests.get(url, timeout=15, proxies=proxies)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", class_="Box-row")

        repos = []
        for article in articles:
            repo = self._parse_article(article)
            if repo:
                repos.append(repo)

        print(f"[Crawler] 解析完成，共 {len(repos)} 个仓库")
        return repos

    def _parse_article(self, article) -> Optional[Repo]:
        """解析单个 article 元素为 Repo 对象"""
        try:
            # 仓库名和链接
            h2 = article.find("h2", class_="h3")
            if not h2:
                return None
            link = h2.find("a")
            if not link:
                return None

            href = link.get("href", "").strip().strip("/")
            parts = href.split("/")
            if len(parts) < 2:
                return None
            owner, name = parts[0], parts[1]

            # 去除 owner 前的空白文本后，link 文本是 "owner / name"
            full_text = link.get_text(strip=True)
            # 如果显示的是 "owner / name"，则提取验证
            if " / " in full_text:
                text_owner, text_name = full_text.split(" / ", 1)
                # 优先使用文本提取的内容
                owner = text_owner.strip()
                name = text_name.strip()

            url = f"https://github.com/{owner}/{name}"

            # 描述
            desc_p = article.find("p", class_=re.compile(r"col-9"))
            description = desc_p.get_text(strip=True) if desc_p else ""

            # 编程语言
            lang_el = article.find("span", itemprop="programmingLanguage")
            language = lang_el.get_text(strip=True) if lang_el else ""

            # 语言颜色
            color_el = article.find("span", class_="repo-language-color")
            language_color = ""
            if color_el:
                style = color_el.get("style", "")
                color_match = re.search(r"background-color:\s*([#\w]+)", style)
                if color_match:
                    language_color = color_match.group(1)

            # 总 Star 数
            stars = ""
            star_link = article.find("a", href=re.compile(r"/stargazers"))
            if star_link:
                stars = star_link.get_text(strip=True)
            else:
                # 备选：找所有带 svg octicon-star 的链接
                star_svg = article.find("svg", class_=lambda c: c and "octicon-star" in c)
                if star_svg:
                    parent = star_svg.find_parent("a")
                    if parent:
                        stars = parent.get_text(strip=True)

            # 今日新增 Star
            stars_today = ""
            for span in article.find_all("span", class_="d-inline-block"):
                text = span.get_text(strip=True)
                if "stars today" in text or "star today" in text:
                    today_match = re.search(r"([\d,]+)\s+stars?\s+today", text)
                    if today_match:
                        stars_today = today_match.group(1)
                    break

            return Repo(
                owner=owner,
                name=name,
                description=description,
                language=language,
                language_color=language_color,
                stars=stars,
                stars_today=stars_today,
                url=url,
            )

        except Exception as e:
            print(f"[Crawler] 解析单个仓库时出错: {e}")
            return None
