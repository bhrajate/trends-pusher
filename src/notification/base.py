"""通知发送器抽象接口"""

from abc import ABC, abstractmethod


class BaseSender(ABC):
    """通知发送器抽象基类"""

    @abstractmethod
    def send(self, content: str) -> bool:
        """发送消息，返回 True 表示成功"""
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
