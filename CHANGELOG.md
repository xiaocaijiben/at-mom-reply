# Changelog

## [1.0.0] - 2026-08-19

- 首次发布
- 新增：群聊中有人 @ bot 时，自动在群内 @ 对方并回复配置文本（默认「妈妈」）。
- 实现：使用 `chat.receive.after_process` 观察模式 Hook 监听消息，不阻塞 LLM 主链路。
- 配置：`reply.at_sender`、`reply.reply_text`、`reply.cooldown_seconds`。
- 兼容：MaiBot Host 1.0.0 ~ 1.2.99，Plugin SDK 2.x。