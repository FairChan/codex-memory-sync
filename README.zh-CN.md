<p align="center">
  <img src="assets/syncmind-logo.png" alt="SyncMind logo" width="996">
</p>

<p align="center">
  <a href="https://github.com/FairChan/codex-memory-sync/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/FairChan/codex-memory-sync?style=social"></a>
  <a href="https://github.com/FairChan/codex-memory-sync/watchers"><img alt="GitHub watchers" src="https://img.shields.io/github/watchers/FairChan/codex-memory-sync?style=social"></a>
</p>

<p align="center">
  <a href="README.md"><kbd>English</kbd></a>
  <a href="README.zh-CN.md"><kbd>简体中文</kbd></a>
  <a href="README.ja.md"><kbd>日本語</kbd></a>
  <a href="README.ms.md"><kbd>Bahasa Melayu</kbd></a>
  <a href="README.ko.md"><kbd>한국어</kbd></a>
  <a href="README.fr.md"><kbd>Français</kbd></a>
  <a href="README.de.md"><kbd>Deutsch</kbd></a>
</p>

# SyncMind

SyncMind 是一个 Codex skill，用来让项目记忆在不同成员、电脑和 Codex 线程之间保持同步。

它不试图让某一次聊天永远记住所有事情。它把工作记忆放进你的仓库，记录每一次记忆变更，并让新线程只读取真正变化的内容。

## 现在的问题

Codex 线程很好用，但它们并不共享同一份实时记忆。

在团队里，这很快会带来麻烦：

- 一个同事的 Codex 不知道另一个同事的 Codex 已经改了什么
- 新线程看不到旧线程里的决定
- 交接信息留在聊天历史里，而不是项目里
- 大家为了找到变更，不得不反复读取大量上下文
- 记忆文件变长后会浪费 token
- 初始化脚本可能不小心覆盖已有笔记

SyncMind 把这些信息写清楚，并让它们进入版本管理。

## 它做了什么

SyncMind 会在项目里添加一个 `.codex-memory/` 文件夹。

这个文件夹保存：

- 当前工作和活跃文件归属
- 每个线程自己的记忆文件
- 交接笔记
- 任务日志
- 决策、风险和部署记录
- 机器可读的记忆提交日志
- 人类可读的记忆提交日志
- 每个线程的同步游标
- 压缩后的摘要和归档

每一次记忆更新都会得到一个编号。每条记录都会写明是谁写的、什么时候写的、哪个线程写的、改了什么，以及下一次应该读取的准确位置。

## 安装

从 GitHub 安装这个 skill：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Windows 通常使用：

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

安装后重启 Codex。

## 开始一个新项目

在一个全新的项目里，可以直接对 Codex 说：

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

也可以直接运行脚本：

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

它会在需要时创建 `.codex-memory/` 和 `AGENTS.md`。

默认不会覆盖已有文件。

## 加入已有项目

如果你的同事已经创建了 `.codex-memory/`，可以对 Codex 说：

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

也可以运行：

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

它会扫描已有记忆。如果项目还没有索引过的记忆提交，它会创建第一条索引记录。

## 用自然语言使用

你不需要记住每一条命令。

开始工作：

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

记录进度：

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

准备交接：

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

压缩过长记忆：

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

导入旧笔记：

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## 直接命令

同步当前线程：

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

读取输出里提示的位置后，将它们标记为已读：

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

提交线程记忆：

```bash
python scripts/memory_sync.py commit \
  --project /path/to/repo \
  --actor "alice" \
  --thread "alice-thread" \
  --summary "Finished login session refresh" \
  --body "Implemented refresh-token happy path and left browser expiry QA as the next step." \
  --files app/auth.ts app/session.ts \
  --tests "auth unit tests passed" \
  --risks "browser expiry flow still needs manual QA" \
  --next "Run browser login regression" \
  --handoff \
  --current
```

压缩记忆：

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

查看状态：

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## 增量同步如何节省上下文

SyncMind 会把每一次记忆变更写入：

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

每条记录包含：

- 记忆编号
- 记忆 ID
- 提交人
- 线程
- 摘要
- 被修改的记忆文件
- 文件里的第几个条目
- 行号范围
- 相关代码文件

所以新线程不需要读取全部记忆文件，只需要读取新条目的准确位置。

示例同步输出：

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## 文件结构

```text
.codex-memory/
  CURRENT_WORK.md
  CURRENT_WORK.codex.md
  HANDOFF.md
  TASK_LOG.md
  DECISIONS.md
  RISKS.md
  DEPLOYMENT.md
  SUMMARY.md
  MEMORY_INDEX.md
  MEMORY_COMMITS.jsonl
  MEMORY_COMMITS.md
  COMPACTION_STATE.json
  THREADS/
  CURSORS/
  ARCHIVE/
  IMPORTED/
```

## 安全性

SyncMind 默认很保守。

- `init` 只创建缺失文件，并保留已有文件
- `adopt` 永远不会覆盖已有记忆
- `import` 会把旧笔记复制到带时间戳的文件夹
- `commit` 只追加新条目
- `compact` 会先归档，再更新摘要
- 正常工作流不需要破坏式替换

## 为什么要做这个

项目记忆最好是可见的。

文件可以 diff、review、commit、回滚和共享。SyncMind 保持这个过程简单：写下发生了什么，记录写在哪里，让下一个线程只读取新的部分。
