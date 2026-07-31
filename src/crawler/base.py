"""爬虫抽象接口与数据模型"""

from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Repo:
    """GitHub 仓库信息"""
    owner: str           # 仓库所有者
    name: str            # 仓库名
    description: str     # 项目描述
    language: str        # 编程语言（可为空）
    language_color: str  # 语言颜色 hex（可为空）
    stars: str           # 总 Star 数（格式化字符串，如 "42.3k"）
    stars_today: str     # 今日新增 Star（格式化字符串）
    url: str             # 仓库 URL

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class BaseCrawler(ABC):
    """爬虫抽象基类"""

    @abstractmethod
    def crawl(self) -> list[Repo]:
        """抓取并返回仓库列表"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称"""
        ...
