# 🔥 Chat Spark｜和你的 GPT 聊天续火花

> 今天和哪条 Chat 续火花了？再多聊几天，说不定就能开船！⛵️

受 QQ 好友互动标识启发，**Chat Spark** 给你的 ChatGPT / Codex 聊天加一点仪式感：常回去聊的对话会亮起火花，连续成为你最常聊的对话还能获得小船和轮船。徽章直接出现在聊天标题后面，例如：

```text
深夜脑洞收容所 🔥🔥
我的学习搭子 🔥🔥🔥 ⛵️
永远聊不完的游戏企划 🔥🔥🔥 🚢
```

## ✨ 怎么点亮？

| 徽章 | 解锁方式 |
| --- | --- |
| 🔥 | 连续 3 天在同一条聊天里发消息 |
| 🔥🔥 | 连续 7 天 |
| 🔥🔥🔥 | 连续 30 天 |
| ⛵️ | 同一条聊天连续 7 天成为你**完成问答轮数最多**的聊天 |
| 🚢 | 把这项“聊天第一名”保持到连续 30 天 |

每天给一条聊天发至少一条消息，就算给它续了当天的火花。一次完成的“你发消息 → 助手回答”算一轮；如果两条聊天并列第一，当天就没有轮船冠军。断更后，火花和轮船会按当前连胜情况重新计算。标题上的徽章会自动更新，你自己起的聊天名字会保留。

## 🚀 开始养火花

1. 下载本仓库，把整个文件夹放到 Codex 的技能目录，路径为 `~/.codex/skills/chat-spark`（如果设置了 `CODEX_HOME`，则使用 `$CODEX_HOME/skills/chat-spark`）。确保 `SKILL.md` 位于这个目录的根部。
2. 在 **Codex 桌面版**聊天中输入：

   ```text
   用 $chat-spark 检查我的聊天火花，并更新符合条件的聊天标题。
   ```

3. 想每天自动续？在 Codex 桌面版中创建每天当地时间 **09:00** 运行的定时任务，提示词可以写：

   ```text
   每天用 $chat-spark 结算昨天的聊天，更新火花和轮船标题。状态文件固定保存在我的工作目录 work/chat-spark-state.json；没有变化时保持安静。
   ```

首次运行时，给状态文件选一个**仓库之外、可长期保留**的位置；以后手动运行或定时运行都沿用同一路径。技能只保存每日发言次数、完成轮数和标题徽章，不保存聊天正文。

## 💬 玩之前知道这些

- 这是**受 QQ 启发的独立小项目**，不连接 QQ，也不会读取 QQ 消息。
- 当前版本使用 Codex 桌面版可访问的聊天工具，范围为**最近 50 条聊天加置顶聊天**。读取不到的聊天会跳过；因此轮船的“第一名”是在已纳入统计的聊天中比较。
- 火花可以根据可读历史补算；轮船连胜从启用当天开始，第一艘小船最早会在 7 天后出现。
- 每天 09:00 结算的是**前一个完整自然日**。今天刚聊的内容，明天结算后才会反映在标题里。

想看具体规则和实现？见 [SKILL.md](SKILL.md) 与 [计分脚本](score.py)。

---

## English · Quick guide

**Chat Spark** is a QQ-inspired Codex desktop skill that adds activity badges to ChatGPT and Codex chat titles. Send a message in the same chat for 3, 7, or 30 consecutive days to earn 🔥, 🔥🔥, or 🔥🔥🔥. A chat that uniquely leads your completed question–answer rounds for 7 consecutive days earns ⛵️; 30 days upgrades it to 🚢.

Install this repository as `chat-spark` in your Codex skills directory, then invoke `$chat-spark` in the Codex desktop app. A daily 09:00 task can settle the previous day automatically. The skill stores daily counts and badge state outside the repository, without saving message bodies. It does not connect to QQ.
