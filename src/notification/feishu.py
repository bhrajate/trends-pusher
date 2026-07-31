"""飞书推送发送器 — 支持交互卡片格式"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import requests

from src.crawler.base import Repo

from .base import BaseSender

MAX_FEISHU_BYTES = 30000


class FeishuSender(BaseSender):
    """通过飞书自定义机器人 webhook 推送"""

    def __init__(
        self,
        webhook_url: str,
        secret: str = "",
        proxy: Optional[str] = None,
    ):
        self._webhook_url = webhook_url
        self._secret = secret
        self._proxy = proxy

    @property
    def channel_name(self) -> str:
        return "飞书"

    @classmethod
    def validate_config(cls, config: dict) -> bool:
        webhook_url = config.get("webhook_url", "")
        return bool(webhook_url and webhook_url.strip())

    def _sign(self) -> tuple[int, str]:
        """生成飞书签名校验"""
        timestamp = int(time.time())
        if not self._secret:
            return timestamp, ""

        string_to_sign = f"{timestamp}\n{self._secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return timestamp, sign

    def send(
        self,
        repos: list[Repo],
        display_cfg: dict[str, Any],
        since: str = "daily",
    ) -> bool:
        """发送飞书交互卡片"""
        max_items = display_cfg.get("max_items", 25)
        repos = repos[:max_items]

        # 构建卡片 JSON
        card = self._build_card(repos, display_cfg, since)
        card_json = json.dumps(card, ensure_ascii=False)

        # 如果卡片内容超长，降级为文本模式
        if len(card_json.encode("utf-8")) > MAX_FEISHU_BYTES:
            print("[飞书] 卡片内容超长，降级为文本模式")
            return self._send_as_text(repos, display_cfg, since)

        return self._send_card(card)

    def _build_card(
        self,
        repos: list[Repo],
        display_cfg: dict[str, Any],
        since: str,
    ) -> dict:
        """构建飞书卡片 2.0"""
        bj_now = datetime.now(timezone.utc) + timedelta(hours=8)
        date_str = bj_now.strftime("%Y-%m-%d")
        since_label = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}.get(
            since, since.capitalize()
        )

        show_desc = display_cfg.get("show_description", True)
        show_color = display_cfg.get("show_language_color", True)

        # 卡片元素列表
        elements = []

        for i, repo in enumerate(repos, 1):
            # 语言标签
            lang_tag = ""
            if show_color and repo.language:
                color = repo.language_color or "#888"
                lang_tag = (
                    f"<font color='{color}'>●</font> "
                    f"**{repo.language}**  "
                )

            # 构建每个仓库的 markdown 块
            lines = [
                f"{lang_tag}[{repo.full_name}]({repo.url})",
            ]

            if show_desc and repo.description:
                desc = repo.description.strip()
                if len(desc) > 150:
                    desc = desc[:147] + "..."
                lines.append(f"{desc}")

            # 统计行
            stats = []
            if repo.stars:
                stats.append(f"⭐ {repo.stars}")
            if repo.stars_today:
                stats.append(f"📈 +{repo.stars_today} today")

            if stats:
                lines[-1] += f"  \n{'  |  '.join(stats)}"

            elements.append({"tag": "markdown", "content": "\n".join(lines)})

            # 分隔线（最后一个不加）
            if i < len(repos):
                elements.append({"tag": "hr"})

        # 底部说明
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"共 {len(repos)} 个项目 · GitHub Trends Pusher",
                }
            ],
        })

        return {
            "schema": "2.0",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🔥 GitHub Trending · {date_str} · {since_label}",
                },
                "template": "indigo",
            },
            "body": {
                "elements": elements,
            },
        }

    def _send_card(self, card: dict) -> bool:
        """发送交互卡片"""
        timestamp, sign = self._sign()

        payload: dict = {
            "timestamp": str(timestamp),
            "msg_type": "interactive",
            "card": card,
        }
        if sign:
            payload["sign"] = sign

        proxies = None
        if self._proxy:
            proxies = {"http": self._proxy, "https": self._proxy}

        try:
            resp = requests.post(
                self._webhook_url, json=payload, timeout=15, proxies=proxies
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print(f"[飞书] 卡片发送成功")
                return True
            else:
                print(f"[飞书] 发送失败: {result.get('msg', '未知错误')}")
                return False
        except requests.RequestException as e:
            print(f"[飞书] 请求失败: {e}")
            return False

    def _send_as_text(
        self,
        repos: list[Repo],
        display_cfg: dict[str, Any],
        since: str,
    ) -> bool:
        """降级：以文本模式发送（超长时使用）"""
        from .formatter import format_trending

        content = format_trending(
            repos,
            channel="feishu",
            max_items=display_cfg.get("max_items", 25),
            show_language_color=display_cfg.get("show_language_color", True),
            show_description=display_cfg.get("show_description", True),
            since=since,
        )

        chunks = self._split_text(content)
        if len(chunks) > 1:
            print(f"[飞书] 消息过长，分 {len(chunks)} 批发送")

        success_count = 0
        for i, chunk in enumerate(chunks, 1):
            timestamp, sign = self._sign()

            if len(chunks) > 1:
                chunk = f"({i}/{len(chunks)})\n{chunk}"

            payload: dict = {
                "timestamp": str(timestamp),
                "msg_type": "text",
                "content": {"text": chunk},
            }
            if sign:
                payload["sign"] = sign

            proxies = None
            if self._proxy:
                proxies = {"http": self._proxy, "https": self._proxy}

            try:
                resp = requests.post(
                    self._webhook_url, json=payload, timeout=15, proxies=proxies
                )
                resp.raise_for_status()
                result = resp.json()
                if result.get("code") == 0:
                    success_count += 1
                else:
                    print(f"[飞书] 第 {i}/{len(chunks)} 批失败: {result.get('msg', '')}")
            except requests.RequestException as e:
                print(f"[飞书] 第 {i}/{len(chunks)} 批请求失败: {e}")

        if success_count == len(chunks):
            print(f"[飞书] 文本发送成功 ({success_count} 批)")
            return True
        else:
            print(f"[飞书] 部分失败: {success_count}/{len(chunks)} 成功")
            return False

    def _split_text(self, content: str) -> list[str]:
        """将超长内容分批"""
        content_bytes = content.encode("utf-8")
        if len(content_bytes) <= MAX_FEISHU_BYTES:
            return [content]

        chunks = []
        lines = content.split("\n")
        current = []
        current_size = 0

        for line in lines:
            line_bytes = (line + "\n").encode("utf-8")
            if current_size + len(line_bytes) > MAX_FEISHU_BYTES:
                if current:
                    chunks.append("\n".join(current))
                current = [line]
                current_size = len(line_bytes)
            else:
                current.append(line)
                current_size += len(line_bytes)

        if current:
            chunks.append("\n".join(current))

        return chunks if chunks else [content]
