"""消息格式化模块 — 将 Repo 列表渲染为渠道 Markdown 消息"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from src.crawler.base import Repo

# 语言 → emoji 颜色映射
LANGUAGE_COLORS: dict[str, str] = {
    "Python": "🐍",
    "JavaScript": "🟨",
    "TypeScript": "🔷",
    "Go": "🩵",
    "Rust": "🦀",
    "Java": "☕",
    "Kotlin": "🟣",
    "Swift": "🟠",
    "C": "🔵",
    "C++": "🔵",
    "C#": "🟢",
    "Ruby": "🔴",
    "PHP": "🟣",
    "R": "📊",
    "Scala": "🔴",
    "Shell": "⬛",
    "PowerShell": "⬛",
    "Dart": "🩵",
    "Lua": "🔵",
    "HTML": "🟠",
    "CSS": "🔵",
    "Vue": "🟢",
    "Jupyter Notebook": "🟠",
    "Objective-C": "🔵",
    "Elixir": "🟣",
    "Haskell": "🟣",
    "Clojure": "🟢",
    "Zig": "🟠",
    "MDX": "⬜",
    "Makefile": "⬜",
    "Dockerfile": "🔵",
}


def _language_emoji(language: str) -> str:
    """获取语言对应的 emoji，未匹配时返回默认值"""
    if not language:
        return "⬜"
    # 精确匹配
    if language in LANGUAGE_COLORS:
        return LANGUAGE_COLORS[language]
    # 不区分大小写匹配
    for key, emoji in LANGUAGE_COLORS.items():
        if key.lower() == language.lower():
            return emoji
    return "⬜"


def format_trending(
    repos: list[Repo],
    channel: str,
    max_items: int = 25,
    show_language_color: bool = True,
    show_description: bool = True,
    since: str = "daily",
) -> str:
    """将仓库列表格式化为推送消息

    Args:
        repos: 仓库列表
        channel: 渠道标识 (feishu, wechat, default)
        max_items: 最大显示条数
        show_language_color: 是否显示语言 emoji
        show_description: 是否显示项目描述
        since: 榜单类型 (daily/weekly/monthly)
    """

    # 截断
    repos = repos[:max_items]

    # 北京时间
    bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
    date_str = bj_now.strftime("%Y-%m-%d")

    since_label = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}.get(
        since, since.capitalize()
    )

    lines = [
        f"🔥 GitHub Trending · {date_str} · {since_label}",
        "",
        "━" * 30,
        "",
    ]

    for i, repo in enumerate(repos, 1):
        # 语言颜色 emoji
        lang_prefix = ""
        if show_language_color and repo.language:
            lang_prefix = f"{_language_emoji(repo.language)} "

        # 仓库名
        lines.append(f"{i}. {lang_prefix}{repo.full_name}")

        # 描述
        if show_description and repo.description:
            # 飞书和微信都支持简单 Markdown
            desc = repo.description.strip()
            if len(desc) > 120:
                desc = desc[:117] + "..."
            lines.append(f"   {desc}")

        # 统计信息
        stats_parts = []
        if repo.stars:
            stats_parts.append(f"⭐ {repo.stars}")
        if repo.stars_today:
            stats_parts.append(f"📈 +{repo.stars_today} today")

        if stats_parts:
            lines.append(f"   {'  |  '.join(stats_parts)}")

        # 链接
        lines.append(f"   🔗 {repo.url}")
        lines.append("")

    lines.append("━" * 30)
    lines.append(f"共 {len(repos)} 个项目 · Powered by GitHub Trends Pusher")

    return "\n".join(lines)
