# Codex Memory Sync Prompts

## 开工

```text
开工。请先 git pull，然后读取 AGENTS.md 和 .codex-memory 下的当前工作记忆。总结现在谁在做什么、我可以安全修改哪些文件、下一步应该做什么。确认后再开始改代码。
```

## 安全初始化

```text
请使用 $codex-memory-sync 初始化这个仓库的外部记忆。先运行 memory_sync.py init --dry-run，说明如果 .codex-memory 已存在会保留哪些文件、会新增哪些文件。确认不会覆盖同事已有内容后再执行初始化。
```

## 接手同事项目

```text
我接手了同事已经有 .codex-memory 的项目。请运行 memory_sync.py adopt --record-existing，不要覆盖任何已有文件；然后告诉我 baseline 应该读哪些文件，以及当前最新记忆提交编号。
```

## 线程同步

```text
这是一个新线程。请运行 memory_sync.py sync --thread "<线程名>"。如果没有游标，只让我读取 SUMMARY.md、CURRENT_WORK.md、MEMORY_INDEX.md；如果有新提交，只列出我需要读取的提交编号、文件、第几个条目和行号范围。
```

## 记忆提交

```text
请用 memory_sync.py commit 提交本线程记忆，写清楚摘要、细节、相关代码文件、测试、风险和下一步。提交后检查是否触发自动压缩，并报告生成的记忆提交编号。
```

## 新任务

```text
我要做：<任务名>。请先在 CURRENT_WORK.md 注册任务、标记 owner、branch、可能修改的文件和 files locked，然后创建任务分支。
```

## 新线程接手

```text
这是新线程。请读取 AGENTS.md 和 .codex-memory，接手 <任务名>，不要依赖旧聊天记录。先复述当前状态、风险和下一步。
```

## 收工

```text
收工。请用 memory_sync.py commit 写入本线程记忆；如果需要交接加 --handoff，如果改变当前任务状态加 --current。记录测试结果、风险、下一步，然后提交并推送。
```

## 交给同事

```text
请把当前进度写入 HANDOFF.md，包括改了什么、为什么、风险、测试结果、下一步。然后提交推送。
```

## 同事接手

```text
开工。请 git pull，读取 .codex-memory/HANDOFF.md，接手 <owner> 的 <任务名>，先复述当前状态和风险。
```

## 冲突检查

```text
继续前请重新读取 .codex-memory，检查是否有其他线程更新过状态，尤其是 Files locked 和 Conflicts，再决定下一步。
```

## 部署后记录

```text
部署完成。请更新 DEPLOYMENT.md，记录部署时间、commit、部署命令、结果和回滚方式。
```
