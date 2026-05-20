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

SyncMind ist ein Codex Skill, der Projektgedächtnis zwischen Personen, Computern und Codex-Threads synchron hält.

Es versucht nicht, einer einzelnen Chat-Sitzung alles für immer merken zu lassen. Stattdessen legt es das Arbeitsgedächtnis im Repository ab, zeichnet jede Änderung daran auf und lässt neue Threads nur lesen, was sich geändert hat.

## Das Problem

Codex-Threads sind nützlich, aber sie teilen nicht dasselbe laufende Gedächtnis.

Im Team wird das schnell mühsam:

- der Codex einer Person weiß nicht, was der Codex einer anderen Person bereits geändert hat
- ein neuer Thread sieht die Entscheidungen des alten Threads nicht
- Handoffs bleiben im Chatverlauf statt im Projekt
- alle lesen zu viel Kontext erneut, nur um Änderungen zu finden
- lange Memory-Dateien verschwenden irgendwann Tokens
- bestehende Notizen können versehentlich durch ein Setup-Skript überschrieben werden

SyncMind macht diese Teile sichtbar und versionierbar.

## Was Es Macht

SyncMind fügt Ihrem Projekt einen Ordner `.codex-memory/` hinzu.

Darin speichert es:

- aktuelle Arbeit und aktive Dateiverantwortung
- Memory-Dateien pro Thread
- Handoff-Notizen
- Task-Logs
- Entscheidungen, Risiken und Deployment-Notizen
- ein maschinenlesbares Memory-Commit-Log
- ein menschenlesbares Memory-Commit-Log
- Sync-Cursor pro Thread
- komprimierte Zusammenfassungen und Archive

Jede Memory-Aktualisierung erhält einen nummerierten Memory-Commit. Jeder Commit hält fest, wer ihn geschrieben hat, wann es passiert ist, welcher Thread ihn geschrieben hat, was sich geändert hat und welche genaue Stelle als Nächstes gelesen werden soll.

## Installation

Installieren Sie den Skill von GitHub:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Unter Windows ist der Befehl normalerweise:

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Starten Sie Codex nach der Installation neu.

## Ein Neues Projekt Starten

In einem neuen Projekt bitten Sie Codex:

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

Oder führen Sie das Skript direkt aus:

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

Das erstellt bei Bedarf `.codex-memory/` und `AGENTS.md`.

Bestehende Dateien werden standardmäßig nicht überschrieben.

## Einem Bestehenden Projekt Beitreten

Wenn ein Teammitglied bereits `.codex-memory/` angelegt hat, bitten Sie Codex:

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

Oder führen Sie aus:

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

Das scannt das vorhandene Gedächtnis und erstellt einen ersten indexierten Memory-Commit, falls noch keiner existiert.

## Nutzung In Natürlicher Sprache

Sie müssen nicht jeden Befehl auswendig kennen.

Arbeit beginnen:

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

Fortschritt festhalten:

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

Handoff vorbereiten:

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

Langes Gedächtnis komprimieren:

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

Alte Notizen importieren:

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## Direkte Befehle

Diesen Thread synchronisieren:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

Nachdem Sie die gemeldeten Stellen gelesen haben, markieren Sie sie als gelesen:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

Thread-Gedächtnis committen:

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

Gedächtnis komprimieren:

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

Status prüfen:

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## Wie Inkrementelle Synchronisierung Kontext Spart

SyncMind schreibt jede Memory-Änderung nach:

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

Jeder Eintrag enthält:

- Memory-Nummer
- Memory-ID
- Actor
- Thread
- Zusammenfassung
- geänderte Memory-Datei
- Eintragsnummer in dieser Datei
- Zeilenbereich
- zugehörige Code-Dateien

Ein neuer Thread kann dadurch nur die genauen neuen Einträge lesen, statt alle Memory-Dateien zu laden.

Beispielausgabe:

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## Dateistruktur

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

## Sicherheit

SyncMind ist standardmäßig vorsichtig.

- `init` erstellt fehlende Dateien und behält bestehende Dateien
- `adopt` überschreibt nie bestehendes Gedächtnis
- `import` kopiert alte Notizen in einen Ordner mit Zeitstempel
- `commit` hängt neue Einträge an
- `compact` archiviert das Gedächtnis, bevor die Zusammenfassung aktualisiert wird
- destruktives Ersetzen gehört nicht zum normalen Workflow

## Warum Es Das Gibt

Projektgedächtnis funktioniert am besten, wenn es sichtbar ist.

Dateien lassen sich leicht diffen, reviewen, committen, zurückrollen und teilen. SyncMind hält den Ablauf einfach: aufschreiben, was sich geändert hat, festhalten, wo es steht, und den nächsten Thread nur die neuen Teile lesen lassen.
