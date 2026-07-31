"""消息格式化 — 按数据源 + 渠道生成 Markdown"""

from .github import format_trending as format_github
from .hackernews import format_hackernews
from .newsnow import format_newsnow

__all__ = ["format_github", "format_hackernews", "format_newsnow"]
