# Codex Memory Sync Prompts

## 开工

```text
开工。请先 git pull，然后读取 AGENTS.md 和 .codex-memory 下的当前工作记忆。总结现在谁在做什么、我可以安全修改哪些文件、下一步应该做什么。确认后再开始改代码。
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
收工。请总结本次改动，更新 .codex-memory 里的工作记忆和交接文档，记录测试结果，然后提交并推送。
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
