"""通知分发器 — 遍历已配置渠道统一发送"""

from typing import Optional

from .base import BaseSender
from .feishu import FeishuSender
from .wechat import WeChatSender


class NotificationDispatcher:
    """根据配置分发通知到各个渠道"""

    def __init__(self, config: dict, proxy: Optional[str] = None):
        """
        Args:
            config: 完整的 notification 配置字典
            proxy: 可选代理地址
        """
        self._config = config
        self._proxy = proxy
        self._senders: list[BaseSender] = []
        self._build_senders()

    def _build_senders(self) -> None:
        """根据配置构建所有启用的发送器"""
        channels = self._config.get("notification", self._config)
        if not channels:
            return

        # 飞书
        feishu_cfg = channels.get("feishu", {})
        if feishu_cfg.get("enabled", False) or (
            "webhook_url" in feishu_cfg and feishu_cfg["webhook_url"]
        ):
            if FeishuSender.validate_config(feishu_cfg):
                self._senders.append(
                    FeishuSender(
                        webhook_url=feishu_cfg["webhook_url"],
                        secret=feishu_cfg.get("secret", ""),
                        proxy=self._proxy,
                    )
                )
                print(f"[Dispatcher] 已注册: 飞书")
            else:
                print(f"[Dispatcher] 飞书配置不完整，跳过")

        # 微信（Server酱）
        wechat_cfg = channels.get("wechat", {})
        if wechat_cfg.get("enabled", False) or (
            "sendkey" in wechat_cfg and wechat_cfg["sendkey"]
        ):
            if WeChatSender.validate_config(wechat_cfg):
                self._senders.append(
                    WeChatSender(
                        sendkey=wechat_cfg["sendkey"],
                        proxy=self._proxy,
                    )
                )
                print(f"[Dispatcher] 已注册: 微信")
            else:
                print(f"[Dispatcher] 微信配置不完整，跳过")

    def dispatch(self, content: str) -> dict[str, bool]:
        """向所有已配置渠道发送消息

        Args:
            content: 格式化后的 Markdown 消息

        Returns:
            {channel_name: success} 字典
        """
        if not self._senders:
            print("[Dispatcher] 没有配置任何通知渠道，跳过发送")
            return {}

        results = {}
        for sender in self._senders:
            print(f"[Dispatcher] 正在发送到 {sender.channel_name}...")
            success = sender.send(content)
            results[sender.channel_name] = success

        # 汇总
        success_count = sum(1 for v in results.values() if v)
        fail_count = len(results) - success_count
        if fail_count == 0:
            print(f"[Dispatcher] 全部渠道发送成功 ({success_count}/{len(results)})")
        else:
            failed = [k for k, v in results.items() if not v]
            print(
                f"[Dispatcher] 发送完成: {success_count}/{len(results)} 成功, "
                f"失败渠道: {', '.join(failed)}"
            )

        return results
