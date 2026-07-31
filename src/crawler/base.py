"""爬虫抽象基类"""

from abc import ABC, abstractmethod
from typing import Any


class BaseCrawler(ABC):
    """爬虫抽象基类 — 每个数据源一个子类"""

    @abstractmethod
    def crawl(self) -> list[Any]:
        """抓取并返回数据列表"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称"""
        ...
