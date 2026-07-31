"""飞书推送发送器"""

import base64
import hashlib
import hmac
import time
from typing import Optional

import requests

from .base import BaseSender

MAX_FEISHU_BYTES = 30000


class FeishuSender(BaseSender):
    """通过飞书自定义机器人 webhook 推送（文本模式）"""

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

    def send(self, content: str) -> bool:
        """发送文本消息到飞书，超长自动分批"""
        chunks = self._split(content)

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
            print(f"[飞书] 发送成功 ({success_count} 批)")
            return True
        else:
            print(f"[飞书] 部分失败: {success_count}/{len(chunks)} 成功")
            return False

    def _split(self, content: str) -> list[str]:
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
