"""通知发送器抽象接口"""

from abc import ABC, abstractmethod
from typing import Any

from src.crawler.base import Repo


class BaseSender(ABC):
    """通知发送器抽象基类

    每个 sender 负责自己的消息格式化，共享 Repo 数据模型。
    """

    @abstractmethod
    def send(
        self,
        repos: list[Repo],
        display_cfg: dict[str, Any],
        since: str = "daily",
    ) -> bool:
        """发送消息，返回 True 表示成功

        Args:
            repos: 仓库列表
            display_cfg: 展示配置 (max_items, show_language_color, show_description)
            since: 榜单类型 (daily/weekly/monthly)
        """
        ...

    @classmethod
    @abstractmethod
    def validate_config(cls, config: dict) -> bool:
        """校验配置是否完整可用，返回 True 表示可以发送"""
        ...

    @property
    @abstractmethod
    def channel_name(self) -> str:
        """渠道名称，用于日志"""
        ...
