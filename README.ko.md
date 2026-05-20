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

SyncMind는 사람, 컴퓨터, Codex 스레드 사이에서 프로젝트 메모리를 동기화하기 위한 Codex skill입니다.

하나의 채팅 세션이 모든 것을 영원히 기억하도록 만들려는 도구가 아닙니다. 작업 메모리를 저장소에 두고, 모든 메모리 변경을 기록하며, 새 스레드가 바뀐 내용만 읽도록 합니다.

## 문제

Codex 스레드는 유용하지만 같은 실시간 메모리를 공유하지 않습니다.

팀에서는 이 문제가 금방 드러납니다.

- 한 팀원의 Codex가 다른 팀원의 Codex가 이미 한 일을 모릅니다
- 새 스레드가 이전 스레드의 결정을 볼 수 없습니다
- 인수인계가 프로젝트가 아니라 채팅 기록에 남습니다
- 변경점을 찾기 위해 너무 많은 컨텍스트를 다시 읽게 됩니다
- 긴 메모리 파일은 결국 token을 낭비합니다
- 설정 스크립트가 기존 노트를 실수로 덮어쓸 수 있습니다

SyncMind는 이런 내용을 명확하게 만들고 버전 관리할 수 있게 합니다.

## 하는 일

SyncMind는 프로젝트에 `.codex-memory/` 폴더를 추가합니다.

그 안에는 다음을 보관합니다.

- 현재 작업과 활성 파일 소유자
- 스레드별 메모리 파일
- 인수인계 노트
- 작업 로그
- 결정, 위험, 배포 기록
- 기계가 읽을 수 있는 메모리 커밋 로그
- 사람이 읽을 수 있는 메모리 커밋 로그
- 스레드별 동기화 커서
- 압축된 요약과 아카이브

모든 메모리 업데이트에는 번호가 붙은 메모리 커밋이 만들어집니다. 각 커밋은 누가, 언제, 어떤 스레드에서, 무엇을 변경했는지와 다음에 읽을 정확한 위치를 기록합니다.

## 설치

GitHub에서 skill을 설치합니다.

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Windows에서는 보통 다음 명령을 사용합니다.

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

설치 후 Codex를 다시 시작하세요.

## 새 프로젝트 시작

완전히 새 프로젝트에서는 Codex에게 이렇게 요청합니다.

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

스크립트를 직접 실행할 수도 있습니다.

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

필요하면 `.codex-memory/`와 `AGENTS.md`를 만듭니다.

기본적으로 기존 파일을 덮어쓰지 않습니다.

## 기존 프로젝트에 참여

팀원이 이미 `.codex-memory/`를 만들었다면 Codex에게 이렇게 요청합니다.

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

또는 다음을 실행합니다.

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

기존 메모리를 스캔하고, 아직 인덱싱된 메모리 커밋이 없다면 첫 기록을 만듭니다.

## 자연어로 사용

모든 명령을 외울 필요는 없습니다.

작업 시작:

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

진행 상황 기록:

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

인수인계 준비:

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

긴 메모리 압축:

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

이전 노트 가져오기:

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## 직접 명령

이 스레드를 동기화합니다.

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

보고된 메모리 위치를 읽은 뒤 읽음으로 표시합니다.

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

스레드 메모리를 커밋합니다.

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

메모리를 압축합니다.

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

상태를 확인합니다.

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## 증분 동기화가 컨텍스트를 아끼는 방식

SyncMind는 모든 메모리 변경을 다음 위치에 씁니다.

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

각 기록에는 다음이 포함됩니다.

- 메모리 번호
- 메모리 ID
- actor
- 스레드
- 요약
- 변경된 메모리 파일
- 해당 파일 안의 엔트리 번호
- 줄 범위
- 관련 코드 파일

그래서 새 스레드는 모든 메모리 파일을 읽지 않고 정확한 새 엔트리만 읽으면 됩니다.

동기화 출력 예:

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## 파일 구조

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

## 안전성

SyncMind는 기본적으로 보수적으로 동작합니다.

- `init`은 없는 파일만 만들고 기존 파일을 유지합니다
- `adopt`는 기존 메모리를 절대 덮어쓰지 않습니다
- `import`는 오래된 노트를 타임스탬프 폴더로 복사합니다
- `commit`은 새 엔트리를 추가합니다
- `compact`는 요약을 업데이트하기 전에 아카이브합니다
- 일반 워크플로에서는 파괴적인 교체를 사용하지 않습니다

## 만든 이유

프로젝트 메모리는 보이는 곳에 있을 때 가장 다루기 쉽습니다.

파일은 diff, review, commit, rollback, 공유가 쉽습니다. SyncMind는 과정을 단순하게 유지합니다. 무엇이 바뀌었는지 쓰고, 어디에 썼는지 기록하고, 다음 스레드가 새 부분만 읽게 합니다.
