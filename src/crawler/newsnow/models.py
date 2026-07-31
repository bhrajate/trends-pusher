"""热榜条目数据模型（通用，适用于所有 NewsNow 平台）"""

from dataclasses import dataclass


@dataclass
class HotItem:
    """热榜条目"""
    title: str          # 标题
    url: str            # 链接
    rank: int           # 排名（从 1 开始）
    heat: str           # 热度值（各平台格式不同，如 "956万"、"🔥"）
    platform: str       # 平台 ID（如 zhihu, douyin）
    platform_name: str  # 平台显示名（如 知乎, 抖音）
