"""@ 即回复「对方妈妈」插件

在群聊中只要有人 @ 到 bot，就会在群里 @ 对方并回复配置的文本。
通过 chat.receive.after_process 观察模式 Hook 监听消息，不阻塞 LLM 主链路。
"""

import time
from typing import Any

from maibot_sdk import Field, HookHandler, MaiBotPlugin, PluginConfigBase
from maibot_sdk.types import HookMode


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__ = "插件"
    __ui_icon__ = "package"
    __ui_order__ = 0

    enabled: bool = Field(default=True, description="是否启用插件")
    config_version: str = Field(default="1.0.0", description="配置版本")


class ReplySectionConfig(PluginConfigBase):
    """回复设置。"""

    __ui_label__ = "回复设置"
    __ui_icon__ = "message-circle"
    __ui_order__ = 1

    at_sender: bool = Field(default=True, description="回复时是否 @ 对方本人（群聊内提醒对方看到）")
    reply_text: str = Field(
        default="妈妈",
        description="被 @ 后回复的文本",
        json_schema_extra={
            "label": "回复文本",
            "placeholder": "请输入回复内容",
        },
    )
    cooldown_seconds: float = Field(
        default=2.0,
        description="同一聊天流内的回复冷却时间（秒），防止刷屏",
        json_schema_extra={
            "label": "冷却时间(秒)",
            "hint": "0 表示不限制",
        },
    )


class AtMomReplyConfig(PluginConfigBase):
    """插件配置。"""

    plugin: PluginSectionConfig = Field(default_factory=PluginSectionConfig)
    reply: ReplySectionConfig = Field(default_factory=ReplySectionConfig)


class AtMomReplyPlugin(MaiBotPlugin):
    """@ bot 自动回复插件。"""

    config_model = AtMomReplyConfig

    def __init__(self) -> None:
        super().__init__()
        self._last_reply_at: dict[str, float] = {}

    async def on_load(self) -> None:
        self.ctx.logger.info("AtMomReply 插件已加载")

    async def on_unload(self) -> None:
        self._last_reply_at.clear()

    @HookHandler(
        hook="chat.receive.after_process",
        mode=HookMode.OBSERVE,
        name="at_mom_reply",
        description="检测群聊中有人 @ bot 时回复「对方妈妈」",
    )
    async def handle_at_message(self, message: Any = None, **kwargs: Any) -> None:
        """监听消息，@ bot 时在群内 @ 对方并回复。"""
        del kwargs

        if not self.config.plugin.enabled:
            return

        if not isinstance(message, dict):
            return

        stream_id = str(message.get("session_id") or "").strip()
        if not stream_id:
            return

        if not message.get("is_at") and not message.get("is_mentioned"):
            return

        message_info = message.get("message_info")
        if not isinstance(message_info, dict):
            message_info = {}

        user_info = message_info.get("user_info")
        if not isinstance(user_info, dict):
            user_info = {}

        user_id = str(user_info.get("user_id") or "").strip()
        if not user_id:
            return

        additional_config = message_info.get("additional_config")
        if not isinstance(additional_config, dict):
            additional_config = {}

        self_id = str(additional_config.get("self_id") or "").strip()
        if self_id and user_id == self_id:
            return

        cooldown_key = f"{stream_id}:{user_id}"
        now = time.time()
        cooldown_seconds = max(0.0, float(self.config.reply.cooldown_seconds or 0))
        last_reply = self._last_reply_at.get(cooldown_key, 0.0)
        if cooldown_seconds > 0 and now - last_reply < cooldown_seconds:
            return

        self._last_reply_at[cooldown_key] = now

        try:
            segments: list[dict[str, Any]] = []
            if self.config.reply.at_sender:
                segments.append({"type": "at", "data": {"target_user_id": user_id}})
            segments.append({"type": "text", "data": self.config.reply.reply_text or "妈妈"})

            await self.ctx.send.hybrid(segments, stream_id)
            self.ctx.logger.info("AtMomReply 已回复: user=%s stream=%s", user_id, stream_id)
        except Exception as exc:
            self.ctx.logger.warning("AtMomReply 回复失败: user=%s error=%s", user_id, exc)

    async def on_config_update(self, scope: str, config_data: dict[str, object], version: str) -> None:
        del scope
        del config_data
        del version

        self._last_reply_at.clear()


def create_plugin() -> AtMomReplyPlugin:
    return AtMomReplyPlugin()