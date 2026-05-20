# Codex Memory Sync Team Protocol

## 目标

把 Codex 的“记忆”从聊天窗口移到仓库里的结构化 Markdown 文件。这样多人、多电脑、多线程协作时，每个 Codex 都能从同一组文件恢复上下文。

## 关键原则

1. 代码以 Git 为准。
2. 工作记忆以 `.codex-memory/` 为准。
3. 聊天历史不作为事实来源。
4. 开工先读记忆，收工先写记忆。
5. 任何跨人、跨电脑、跨线程交接都必须写入 `HANDOFF.md`。

## 推荐目录

```text
project-root/
  AGENTS.md
  .codex-memory/
    CURRENT_WORK.md
    CURRENT_WORK.codex.md
    HANDOFF.md
    TASK_LOG.md
    DECISIONS.md
    RISKS.md
    DEPLOYMENT.md
    MEMORY_COMMITS.jsonl
    MEMORY_COMMITS.md
    MEMORY_INDEX.md
    SUMMARY.md
    COMPACTION_STATE.json
    THREADS/
    CURSORS/
    ARCHIVE/
    IMPORTED/
```

## 初始化安全规则

默认初始化和接手都是非破坏性的：

```text
如果 .codex-memory/ 不存在：
- 创建目录
- 创建所有 starter 记忆文件
- 创建 THREADS/.gitkeep
- 如果 AGENTS.md 不存在，创建 AGENTS.md

如果 .codex-memory/ 已经存在：
- 保留目录
- 已存在的记忆文件一律不覆盖
- 只补齐缺失的记忆文件
- 同事已经写进去的工作流程不会被覆盖

如果 AGENTS.md 已经存在：
- 如果没有 Codex Memory Sync 管理区块，先备份，再追加管理区块
- 如果已经有管理区块，默认不改
```

接手同事项目：

```text
python scripts/memory_sync.py adopt --project /path/to/repo --actor "你的名字" --thread "你的线程名" --record-existing
```

这会扫描已有记忆并生成一条 adoption 记忆提交，之后新线程只需要根据提交日志增量读取。

`--replace-existing` 只用于明确的修复场景。正常协作不要用它。

重要仓库建议先跑：

```text
python scripts/init_memory_sync.py --project /path/to/repo --dry-run
```

## 记忆提交日志

每次记忆提交都会写入：

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

每条提交记录：

```text
第几条记忆提交 sequence
提交 ID
时间
提交人
线程 ID
用途 purpose
摘要 summary
修改了哪些记忆文件
每个文件里的第几个条目 entry_number
行号范围 start_line/end_line
相关代码文件
当前 Git 分支和 commit
```

新线程启动时先运行：

```text
python scripts/memory_sync.py sync --project /path/to/repo --thread "线程名"
```

如果已有游标，只会列出新的记忆提交和精确位置，不需要读取全部记忆。

读完后运行：

```text
python scripts/memory_sync.py sync --project /path/to/repo --thread "线程名" --mark-seen
```

这样下次只会看到更新后的提交。

## 记忆压缩

`memory_sync.py commit` 默认会在记忆过长时自动触发压缩。压缩会：

```text
1. 把长记忆归档到 .codex-memory/ARCHIVE/
2. 更新 .codex-memory/SUMMARY.md
3. 写入一条 compact 记忆提交
4. 更新 COMPACTION_STATE.json，避免每次重复压缩
```

手动压缩：

```text
python scripts/memory_sync.py compact --project /path/to/repo --actor "你的名字" --thread "线程名"
```

强制压缩：

```text
python scripts/memory_sync.py compact --project /path/to/repo --actor "你的名字" --thread "线程名" --force
```

## 每日开工流程

```text
1. git pull
2. 读取 AGENTS.md
3. 运行 memory_sync.py sync --thread <线程名>
4. 如果没有游标，只读 SUMMARY.md、CURRENT_WORK.md、MEMORY_INDEX.md
5. 如果有新提交，只读 sync 输出的文件位置和行号范围
6. 总结当前任务、owner、locked files、风险和下一步
7. 确认没有文件冲突后再编辑代码
```

推荐口令：

```text
开工。请先 git pull，然后读取 AGENTS.md 和 .codex-memory 下的当前工作记忆。总结现在谁在做什么、我可以安全修改哪些文件、下一步应该做什么。确认后再开始改代码。
```

## 每日收工流程

```text
1. 总结本次修改
2. 使用 memory_sync.py commit 写入线程记忆
3. 如果有人或新线程可能接手，加 --handoff
4. 如果影响当前任务状态，加 --current
5. 如果有部署，记录 DEPLOYMENT.md 后把该文件作为 --memory-files 提交
6. 运行测试或记录未测试原因
7. git status
8. commit
9. push
```

推荐口令：

```text
收工。请用 memory_sync.py commit 写入本线程记忆，记录测试、风险、下一步和相关文件；如记忆过长让自动压缩执行，然后提交并推送。
```

## 文件占用规则

每个 active task 必须写：

```text
Owner
Branch
Files touched
Files locked
Current state
Next step
Blockers
```

如果文件在别人的 `Files locked` 中，另一个 Codex 不应直接修改。必须先记录冲突并等待人类确认。

## 分支规则

推荐每人每任务一个分支：

```text
codex/user-a-login-session
codex/user-b-order-filter
codex/user-a-ui-polish
```

不要让两个人长期直接改 `main`。合并前让 Codex 做一次 review，重点看冲突、遗漏测试和行为回归。

## 服务器部署规则

服务器不要作为多人同时编辑的工作区。推荐流程：

```text
本地或开发分支修改
测试通过
合并到 main
服务器 git pull
执行部署命令
更新 DEPLOYMENT.md
```

`DEPLOYMENT.md` 必须记录部署时间、commit、执行人、命令、结果和回滚方式。

## 同电脑多线程规则

同一台电脑的不同 Codex 线程也必须通过 `.codex-memory/` 同步：

```text
新线程启动：先读 .codex-memory
老线程超过 30 分钟继续工作：重新读 .codex-memory
任何线程完成工作：写回 .codex-memory
```

推荐口令：

```text
继续前请重新读取 .codex-memory，检查是否有其他线程更新过状态，再决定下一步。
```

## 冲突处理

当发现冲突：

```text
1. 停止修改
2. 列出冲突文件
3. 说明自己想改什么
4. 读取对方任务记录
5. 给出合并方案
6. 等待人类确认
7. 再执行
```

把冲突写入 `CURRENT_WORK.md` 的 `Conflicts` 区域。
