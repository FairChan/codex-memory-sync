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

SyncMind は、人、コンピューター、Codex スレッドの間でプロジェクトの作業メモリを同期するための Codex skill です。

ひとつのチャットセッションにすべてを覚えさせるのではありません。作業メモリをリポジトリに置き、すべての変更を記録し、新しいスレッドが変更分だけを読めるようにします。

## 課題

Codex のスレッドは便利ですが、同じライブメモリを共有しているわけではありません。

チームでは、すぐに次のような問題になります。

- あるメンバーの Codex が、別のメンバーの Codex の作業を知らない
- 新しいスレッドが古いスレッドの判断を見られない
- 引き継ぎがプロジェクトではなくチャット履歴に残る
- 変更点を探すために大量の文脈を読み直す必要がある
- メモリファイルが長くなり、token を無駄にする
- セットアップスクリプトが既存のメモを上書きする可能性がある

SyncMind はそれらを明示し、バージョン管理できる形にします。

## できること

SyncMind はプロジェクトに `.codex-memory/` フォルダーを追加します。

その中には次のものを保存します。

- 現在の作業とアクティブなファイル所有者
- スレッドごとのメモリファイル
- 引き継ぎメモ
- タスクログ
- 決定、リスク、デプロイ記録
- 機械が読めるメモリコミットログ
- 人が読めるメモリコミットログ
- スレッドごとの同期カーソル
- 圧縮されたサマリーとアーカイブ

すべてのメモリ更新には番号付きのメモリコミットが作られます。誰が、いつ、どのスレッドで、何を変更したか、次に読むべき正確な場所まで記録します。

## インストール

GitHub から skill をインストールします。

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Windows では通常、次のコマンドを使います。

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

インストール後に Codex を再起動してください。

## 新しいプロジェクトで始める

まっさらなプロジェクトでは、Codex にこう依頼します。

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

直接スクリプトを実行することもできます。

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

必要に応じて `.codex-memory/` と `AGENTS.md` を作成します。

既存ファイルはデフォルトで上書きしません。

## 既存プロジェクトに参加する

チームメイトがすでに `.codex-memory/` を作っている場合は、Codex にこう依頼します。

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

または次を実行します。

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

既存メモリをスキャンし、まだ索引付きのメモリコミットがない場合は最初の記録を作ります。

## 自然言語で使う

すべてのコマンドを覚える必要はありません。

作業を始める：

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

進捗を記録する：

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

引き継ぎを準備する：

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

長いメモリを圧縮する：

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

古いメモを取り込む：

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## 直接コマンド

このスレッドを同期します。

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

表示された場所を読んだら、既読にします。

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

スレッドメモリをコミットします。

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

メモリを圧縮します。

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

状態を確認します。

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## 増分同期で文脈を節約する仕組み

SyncMind はすべてのメモリ変更を次に書き込みます。

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

各レコードには次が含まれます。

- メモリ番号
- メモリ ID
- actor
- スレッド
- サマリー
- 変更されたメモリファイル
- そのファイル内のエントリ番号
- 行範囲
- 関連コードファイル

そのため新しいスレッドは、すべてのメモリファイルではなく、必要な新しいエントリだけを読めます。

同期出力の例：

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## ファイル構成

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

SyncMind はデフォルトで慎重に動きます。

- `init` は不足しているファイルだけを作成し、既存ファイルを残します
- `adopt` は既存メモリを上書きしません
- `import` は古いメモをタイムスタンプ付きフォルダーにコピーします
- `commit` は新しいエントリを追記します
- `compact` はサマリー更新前にアーカイブします
- 通常のワークフローでは破壊的な置き換えは使いません

## なぜ作ったか

プロジェクトメモリは、見える場所にあるほうが扱いやすいです。

ファイルなら diff、review、commit、rollback、共有ができます。SyncMind は流れを単純に保ちます。何が変わったかを書き、どこに書いたかを記録し、次のスレッドには新しい部分だけを読ませます。
