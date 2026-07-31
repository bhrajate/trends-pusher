"""Hacker News → 渠道 Markdown"""

from datetime import datetime, timezone, timedelta

from src.crawler.hackernews import Story

_RANK = {1: "🥇", 2: "🥈", 3: "🥉"}


def _heat(points: int) -> str:
    if points >= 500:
        return "🔥🔥"
    elif points >= 300:
        return "🔥"
    elif points >= 150:
        return "📈"
    elif points >= 70:
        return "📊"
    return "📌"


def format_hackernews(
    stories: list[Story],
    max_items: int = 20,
) -> str:
    stories = stories[:max_items]

    bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
    date_str = bj_now.strftime("%Y-%m-%d")

    lines = [
        f"🔶 Hacker News Frontpage · {date_str}",
        "",
    ]

    for i, story in enumerate(stories, 1):
        rank = _RANK.get(i, f"{i}.")
        heat = _heat(int(story.points)) if story.points else ""

        lines.append(f"**{rank} {heat} [{story.title}]({story.url})**")

        stats = []
        if story.points:
            stats.append(f"⬆ {story.points} points")
        if story.author:
            stats.append(f"by {story.author}")
        if story.comments:
            stats.append(f"💬 {story.comments} comments")
        lines.append("  ·  ".join(stats))

        meta = []
        if story.source:
            meta.append(f"🌐 {story.source}")
        meta.append(f"[HN 讨论]({story.comments_url})")
        lines.append("  |  ".join(meta))

        if i < len(stories):
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("")
    lines.append(f"*共 {len(stories)} 篇文章 · Powered by GitHub Trends Pusher*")

    return "\n".join(lines)
