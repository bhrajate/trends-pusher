"""NewsNow 热榜 → 渠道 Markdown"""

from datetime import datetime, timezone, timedelta

from src.crawler.newsnow import HotItem

# 平台 emoji
_PLATFORM_EMOJI: dict[str, str] = {
    "zhihu": "💡",
    "weibo": "📢",
    "douyin": "🎵",
    "baidu": "🔍",
    "toutiao": "📰",
    "bilibili-hot-search": "📺",
    "wallstreetcn-hot": "📈",
    "thepaper": "🗞",
    "cls-hot": "📊",
    "ifeng": "🦅",
    "tieba": "💬",
    "juejin": "⛏️",
    "nowcoder": "💻",
    "producthunt": "🦄",
}


def format_newsnow(
    items: list[HotItem],
    max_items: int = 20,
) -> str:
    items = items[:max_items]

    if not items:
        return "暂无热榜数据"

    platform_name = items[0].platform_name
    emoji = _PLATFORM_EMOJI.get(items[0].platform, "🔥")
    bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
    date_str = bj_now.strftime("%Y-%m-%d")

    lines = [
        f"{emoji} {platform_name}热榜 · {date_str} · Daily",
        "",
    ]

    for item in items:
        lines.append(f"**{item.rank}. [{item.title}]({item.url})**")
        if item.heat:
            lines.append(f"🔥 {item.heat}")

        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"*共 {len(items)} 条 · Powered by GitHub Trends Pusher*")

    return "\n".join(lines)
