"""GitHub Trending → 渠道 Markdown"""

from datetime import datetime, timezone, timedelta

from src.crawler.github import Repo

LANGUAGE_COLORS: dict[str, str] = {
    "Python": "🐍", "JavaScript": "🟨", "TypeScript": "🔷",
    "Go": "🩵", "Rust": "🦀", "Java": "☕", "Kotlin": "🟣",
    "Swift": "🟠", "C": "🔵", "C++": "🔵", "C#": "🟢",
    "Ruby": "🔴", "PHP": "🟣", "R": "📊", "Scala": "🔴",
    "Shell": "⬛", "PowerShell": "⬛", "Dart": "🩵",
    "Lua": "🔵", "HTML": "🟠", "CSS": "🔵", "Vue": "🟢",
    "Jupyter Notebook": "🟠", "Objective-C": "🔵",
    "Elixir": "🟣", "Haskell": "🟣", "Clojure": "🟢",
    "Zig": "🟠", "MDX": "⬜", "Makefile": "⬜", "Dockerfile": "🔵",
}


def _lang_emoji(language: str) -> str:
    if not language:
        return "⬜"
    if language in LANGUAGE_COLORS:
        return LANGUAGE_COLORS[language]
    for k, v in LANGUAGE_COLORS.items():
        if k.lower() == language.lower():
            return v
    return "⬜"


def format_trending(
    repos: list[Repo],
    max_items: int = 25,
    show_language_color: bool = True,
    show_description: bool = True,
    since: str = "daily",
) -> str:
    repos = repos[:max_items]

    bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
    date_str = bj_now.strftime("%Y-%m-%d")
    since_label = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}.get(
        since, since.capitalize()
    )

    lines = [
        f"🔥 GitHub Trending · {date_str} · {since_label}",
        "",
    ]

    for i, repo in enumerate(repos, 1):
        emoji = _lang_emoji(repo.language) if show_language_color and repo.language else ""
        lines.append(f"**{i}. {emoji} [{repo.full_name}]({repo.url})**")

        if show_description and repo.description:
            desc = repo.description.strip()
            if len(desc) > 120:
                desc = desc[:117] + "..."
            lines.append(desc)

        stats = []
        if repo.stars:
            stats.append(f"⭐ {repo.stars}")
        if repo.stars_today:
            stats.append(f"📈 +{repo.stars_today} today")
        if stats:
            lines.append("  |  ".join(stats))

        if i < len(repos):
            lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("")
    lines.append(f"*共 {len(repos)} 个项目 · Powered by Trends Pusher*")

    return "\n".join(lines)
