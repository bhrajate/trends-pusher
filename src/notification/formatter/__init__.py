"""消息格式化 — 按数据源 + 渠道生成 Markdown"""

from .github import format_trending as format_github
from .hackernews import format_hackernews

__all__ = ["format_github", "format_hackernews"]
