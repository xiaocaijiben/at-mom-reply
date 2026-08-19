# @ 即回复「妈妈」插件

群聊中只要有人 @ 到 bot，bot 就会在群里 @ 对方并回复文本「妈妈」。
（本插件和此文档使用deepseek-v4-flash生成）

- 适用 MaiBot：Host ≥ 1.0.0，≤ 1.2.99
- 适用 SDK：Maibot Plugin SDK 2.x（Python ≥ 3.10）
- 许可证：MIT

## 功能

- 仅群聊 @ 触发，私聊不回复
- 回复时 @ 对方本人（可在配置中关闭），确保群里能提醒到
- 内置冷却时间，防止刷屏
- 自动跳过 bot 自己发送的消息，避免死循环
- 实现方式为 `chat.receive.after_process` 观察模式 Hook，后台 fire-and-forget，不阻塞 LLM 主链路

## 安装

从本仓库下载最新发布包，将 `at_mom_reply` 目录放到 MaiBot 的 `plugins/` 目录下：

```bash

git clone https://github.com/xiaocaijiben/at-mom-reply temp_repo
cp -r temp_repo/at_mom_reply <你的MaiBot目录>/plugins/
```

然后：

1. 在 WebUI 插件市场中启用本插件。
2. 在插件配置中确认 `plugin.enabled = true`。
3. 在群里 @ bot 测试。

## 配置

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `plugin.enabled` | bool | `true` | 是否启用插件 |
| `plugin.config_version` | string | `1.0.0` | 配置版本，勿随意修改 |
| `reply.at_sender` | bool | `true` | 回复时是否 @ 对方本人 |
| `reply.reply_text` | string | `妈妈` | 被 @ 后回复的文本 |
| `reply.cooldown_seconds` | float | `2.0` | 同一聊天流 + 同一用户内回复冷却时间（秒），`0` 表示不限制 |

配置可在 WebUI 插件配置页修改，也可直接编辑 `config.toml`：

```toml
[plugin]
enabled = true
config_version = "1.0.0"

[reply]
at_sender = true
reply_text = "妈妈"
cooldown_seconds = 2.0
```

## 行为说明

- 触发条件：群聊中有人 @ 到 bot（以适配器提供的 `is_at` 标记为准，支持 NapCat / SnowLuma）。
- 回复形式：`@对方 + 回复文本`，通过 `send.hybrid` 发送。
- 日志关键字：`AtMomReply`，可在 MaiBot 插件运行日志中检索。

## 常见问题

**没有回复？**

- 确认插件已启用且 `plugin.enabled = true`。
- 确认消息确实 @ 了 bot（在群里用 @ 选中 bot 再发送）。
- 确认群聊消息没有被主程序的聊天名单过滤丢弃。
- 检查运行日志中是否有 `Host 丢弃了...`、`AtMomReply 回复失败` 等提示。

**回复出现在私聊？**

- 本插件只处理带 `is_at` 标记的群聊消息，私聊消息不会触发。若适配器把私聊消息也带上了 `is_at`，请在该适配器配置中关闭私聊 @ 检测。

## 兼容性说明

- 当前版本的 MaiBot Host（1.2.0 及相近版本）中，`ON_MESSAGE` 事件处理器在消息链路内已被注释，事件方式不生效。因此本插件采用 `chat.receive.after_process` Hook，这也是戳一戳类插件的通用做法。
- 不同 MaiBot 版本可能调整 Hook 名称或能力申请方式，遇到不兼容请查看 `_manifest.json` 的 `host_application` 范围并升级插件版本。

## 开发

```bash
# 语法检查
python -m compileall at_mom_reply

# 本地验证 manifest
python -c "import json; json.load(open('at_mom_reply/_manifest.json', encoding='utf-8')); print('ok')"
```

## 变更日志

见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

[MIT](LICENSE)
