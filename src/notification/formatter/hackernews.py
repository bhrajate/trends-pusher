"""Hacker News → 渠道 Markdown"""

from datetime import datetime, timezone, timedelta

from src.crawler.hackernews import Story

# 得分热度标识
def _heat_emoji(points: int) -> str:
    if points >= 500:
        return "🔥🔥"
    elif points >= 300:
        return "🔥"
    elif points >= 150:
        return "📈"
    elif points >= 70:
        return "📊"
    else:
        return "📌"

# 排名奖牌
_RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def format_hackernews(
    stories: list[Story],
    max_items: int = 20,
) -> str:
    """将 Hacker News 文章列表格式化为推送消息

    Args:
        stories: 文章列表（按得分降序）
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
        # 排名序号：前三名用奖牌
        rank = _RANK_MEDALS.get(i, f"{i}.")

        # 热度标识
        heat = _heat_emoji(int(story.points)) if story.points else ""

        # 标题行
        lines.append(f"{rank} {heat} [{story.title}]({story.url})")

        # 统计行
        stats = []
        if story.points:
            stats.append(f"**{story.points}** points")
        if story.author:
            stats.append(f"by {story.author}")
        if story.comments:
            stats.append(f"💬 {story.comments} comments")

        lines.append(f"    {'  ·  '.join(stats)}")

        # 来源 + 评论链接
        links = []
        if story.source:
            links.append(f"🌐 {story.source}")
        links.append(f"[HN 讨论]({story.comments_url})")
        lines.append(f"    {'  |  '.join(links)}")

        lines.append("")

    lines.append("━" * 30)
    lines.append(f"共 {len(stories)} 篇文章 · Powered by GitHub Trends Pusher")

    return "\n".join(lines)
