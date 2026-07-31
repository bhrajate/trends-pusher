"""GitHub Trends Pusher — 入口

用法:
  uv run python -m src                        # 默认 GitHub Trending
  uv run python -m src --source github         # GitHub Trending
  uv run python -m src --source hackernews     # Hacker News
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import yaml

from src.crawler.github import GitHubTrendingCrawler
from src.crawler.hackernews import HackerNewsCrawler
from src.crawler.newsnow import NewsNowCrawler
from src.notification.dispatcher import NotificationDispatcher
from src.notification.formatter import format_github
from src.notification.formatter import format_hackernews
from src.notification.formatter import format_newsnow


def _load_config() -> dict:
    """加载配置: YAML 文件 → 环境变量覆盖"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    if not config_path.exists():
        print(f"[Config] 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print(f"[Config] 已加载: {config_path}")

    _override_from_env(config)
    return config


def _override_from_env(config: dict) -> None:
    """用环境变量覆盖配置值"""
    env_map = {
        "FEISHU_ENABLED": ("notification", "feishu", "enabled"),
        "FEISHU_WEBHOOK_URL": ("notification", "feishu", "webhook_url"),
        "FEISHU_SECRET": ("notification", "feishu", "secret"),
        "WECHAT_ENABLED": ("notification", "wechat", "enabled"),
        "WECHAT_SENDKEY": ("notification", "wechat", "sendkey"),
        "CRAWLER_SINCE": ("crawler", "since"),
        "CRAWLER_LANGUAGE": ("crawler", "language"),
        "CRAWLER_SPOKEN_LANGUAGE": ("crawler", "spoken_language"),
        "DISPLAY_MAX_ITEMS": ("display", "max_items"),
    }

    for env_var, path in env_map.items():
        value = os.environ.get(env_var, "").strip()
        if not value:
            continue
        if env_var.endswith("_ENABLED"):
            value = value.lower() in ("true", "1", "yes")
        section = config
        for key in path[:-1]:
            if key not in section:
                section[key] = {}
            section = section[key]
        section[path[-1]] = value


def _get_proxy() -> Optional[str]:
    """获取代理配置"""
    is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    if is_github_actions:
        return None
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if proxy:
        print(f"[Config] 使用代理: {proxy}")
    return proxy


def main():
    parser = argparse.ArgumentParser(description="GitHub Trends Pusher")
    parser.add_argument(
        "--source",
        choices=["github", "hackernews", "newsnow"],
        default="github",
        help="数据源 (default: github)",
    )
    parser.add_argument(
        "--platform",
        default="",
        help="NewsNow 平台 ID (如 zhihu, douyin, juejin, producthunt)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print(f"  Trends Pusher v0.1.0  [{args.source}]")
    print("=" * 50)
    print()

    # 1. 配置
    config = _load_config()
    proxy = _get_proxy()
    display_cfg = config.get("display", {})
    notification_cfg = config.get("notification", {})

    # 2. 抓取 + 格式化（按数据源分发）
    print()
    if args.source == "github":
        crawler_cfg = config.get("crawler", {})
        crawler = GitHubTrendingCrawler(
            since=crawler_cfg.get("since", "daily"),
            language=crawler_cfg.get("language", ""),
            spoken_language=crawler_cfg.get("spoken_language", ""),
            proxy=proxy,
        )
        repos = crawler.crawl()
        if not repos:
            print("[Main] 未抓取到任何仓库，退出")
            sys.exit(0)

        content = format_github(
            repos,
            max_items=display_cfg.get("max_items", 25),
            show_language_color=display_cfg.get("show_language_color", True),
            show_description=display_cfg.get("show_description", True),
            since=crawler_cfg.get("since", "daily"),
        )

    elif args.source == "hackernews":
        crawler = HackerNewsCrawler(proxy=proxy)
        stories = crawler.crawl()
        if not stories:
            print("[Main] 未抓取到任何文章，退出")
            sys.exit(0)

        content = format_hackernews(
            stories,
            max_items=display_cfg.get("max_items", 20),
        )

    elif args.source == "newsnow":
        if not args.platform:
            print("[Main] 使用 --source newsnow 时必须指定 --platform (如 zhihu, juejin, producthunt)")
            sys.exit(1)

        crawler = NewsNowCrawler(platform=args.platform, proxy=proxy)
        items = crawler.crawl()
        if not items:
            print("[Main] 未抓取到任何热榜数据，退出")
            sys.exit(0)

        content = format_newsnow(
            items,
            max_items=display_cfg.get("max_items", 20),
        )

    else:
        print(f"[Main] 未知数据源: {args.source}")
        sys.exit(1)

    # 3. 分发
    print()
    dispatcher = NotificationDispatcher(
        config={"notification": notification_cfg},
        proxy=proxy,
    )
    results = dispatcher.dispatch(content)

    # 4. 汇总
    print()
    if results:
        success = sum(1 for v in results.values() if v)
        if success == len(results):
            print(f"[Main] ✓ 全部 {len(results)} 个渠道发送成功")
        else:
            print(f"[Main] ⚠ {success}/{len(results)} 个渠道发送成功")
    else:
        print("[Main] 没有配置任何通知渠道")

    print()
    print("=" * 50)
    print("  Done.")
    print("=" * 50)


if __name__ == "__main__":
    main()
