"""GitHub Trends Pusher — 入口

流程: 加载配置 → 抓取 Trending → 格式化消息 → 分发到各渠道
"""

import os
import sys
from pathlib import Path
from typing import Optional

import yaml

from src.crawler.github_trending import GitHubTrendingCrawler
from src.formatter import format_trending
from src.notification.dispatcher import NotificationDispatcher


def _load_config() -> dict:
    """加载配置: YAML 文件 → 环境变量覆盖"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    if not config_path.exists():
        print(f"[Config] 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print(f"[Config] 已加载: {config_path}")

    # 环境变量覆盖
    _override_from_env(config)

    return config


def _override_from_env(config: dict) -> None:
    """用环境变量覆盖配置值"""
    env_map = {
        # 飞书
        "FEISHU_ENABLED": ("notification", "feishu", "enabled"),
        "FEISHU_WEBHOOK_URL": ("notification", "feishu", "webhook_url"),
        "FEISHU_SECRET": ("notification", "feishu", "secret"),
        # 微信
        "WECHAT_ENABLED": ("notification", "wechat", "enabled"),
        "WECHAT_SENDKEY": ("notification", "wechat", "sendkey"),
        # 抓取
        "CRAWLER_SINCE": ("crawler", "since"),
        "CRAWLER_LANGUAGE": ("crawler", "language"),
        "CRAWLER_SPOKEN_LANGUAGE": ("crawler", "spoken_language"),
        # 展示
        "DISPLAY_MAX_ITEMS": ("display", "max_items"),
    }

    for env_var, path in env_map.items():
        value = os.environ.get(env_var, "").strip()
        if not value:
            continue

        # 布尔值转换
        if env_var.endswith("_ENABLED"):
            value = value.lower() in ("true", "1", "yes")

        # 设置到配置树
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

    # 本地环境检查代理
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if proxy:
        print(f"[Config] 使用代理: {proxy}")
    return proxy


def main():
    """主流程"""
    print("=" * 50)
    print("  GitHub Trends Pusher v0.1.0")
    print("=" * 50)
    print()

    # 1. 加载配置
    config = _load_config()
    proxy = _get_proxy()

    crawler_cfg = config.get("crawler", {})
    display_cfg = config.get("display", {})
    notification_cfg = config.get("notification", {})

    # 2. 抓取
    print()
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

    # 3. 格式化
    print()
    content = format_trending(
        repos,
        max_items=display_cfg.get("max_items", 25),
        show_language_color=display_cfg.get("show_language_color", True),
        show_description=display_cfg.get("show_description", True),
        since=crawler_cfg.get("since", "daily"),
    )

    # 4. 发送
    print()
    dispatcher = NotificationDispatcher(
        config={"notification": notification_cfg},
        proxy=proxy,
    )
    results = dispatcher.dispatch(content)

    # 5. 汇总
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
