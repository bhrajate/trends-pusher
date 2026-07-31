"""Hacker News → 渠道 Markdown"""

from datetime import datetime, timezone, timedelta

from src.crawler.hackernews import Story


def format_hackernews(
    stories: list[Story],
    max_items: int = 20,
) -> str:
    """将 Hacker News 文章列表格式化为推送消息

    Args:
        stories: 文章列表
        max_items: 最大显示条数
    """

    stories = stories[:max_items]

    bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
    date_str = bj_now.strftime("%Y-%m-%d %H:%M")

    lines = [
        f"🔶 Hacker News Frontpage · {date_str}",
        "",
        "━" * 30,
        "",
    ]

    for i, story in enumerate(stories, 1):
        lines.append(f"{i}. [{story.title}]({story.url})")

        stats_parts = []
        if story.points:
            stats_parts.append(f"⬆ {story.points}")
        if story.comments:
            stats_parts.append(f"💬 {story.comments}")
        if story.source:
            stats_parts.append(f"🔗 {story.source}")

        if stats_parts:
            lines.append(f"   {'  |  '.join(stats_parts)}")

        lines.append(f"   [HN 评论]({story.comments_url})")
        lines.append("")

    lines.append("━" * 30)
    lines.append(f"共 {len(stories)} 篇文章 · Powered by GitHub Trends Pusher")

    return "\n".join(lines)
