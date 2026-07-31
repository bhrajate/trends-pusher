"""Hacker News 文章数据模型"""

from dataclasses import dataclass


@dataclass
class Story:
    """Hacker News 文章"""
    title: str        # 文章标题
    url: str          # 文章链接（或 HN 评论页链接）
    points: str       # 得分（如 "42"）
    author: str       # 作者
    comments: str     # 评论数（如 "15"）
    comments_url: str  # HN 评论页链接
    source: str       # 域名简称（如 "github.com"）
