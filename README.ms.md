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

SyncMind ialah Codex skill untuk menyelaraskan memori projek antara ahli pasukan, komputer, dan thread Codex.

Ia tidak cuba membuat satu sesi chat mengingati semuanya selama-lamanya. Sebaliknya, ia meletakkan memori kerja di dalam repositori anda, merekod setiap perubahan memori, dan membolehkan thread baharu membaca hanya perkara yang berubah.

## Masalah

Thread Codex memang berguna, tetapi ia tidak berkongsi memori hidup yang sama.

Dalam pasukan, perkara ini cepat menjadi masalah:

- Codex seorang rakan pasukan tidak tahu apa yang sudah dibuat oleh Codex rakan lain
- thread baharu tidak dapat melihat keputusan daripada thread lama
- nota handoff tinggal dalam sejarah chat, bukan dalam projek
- semua orang membaca terlalu banyak konteks hanya untuk mencari perubahan
- fail memori yang panjang akhirnya membazir token
- nota sedia ada boleh tertimpa secara tidak sengaja oleh skrip setup

SyncMind menjadikan perkara ini jelas dan boleh dijejaki dalam versi.

## Apa Yang Ia Lakukan

SyncMind menambah folder `.codex-memory/` ke dalam projek anda.

Di dalam folder itu, ia menyimpan:

- kerja semasa dan pemilikan fail aktif
- fail memori bagi setiap thread
- nota handoff
- log tugas
- keputusan, risiko, dan nota deployment
- log memory commit yang boleh dibaca mesin
- log memory commit yang boleh dibaca manusia
- cursor sync bagi setiap thread
- ringkasan dan arkib yang telah dipadatkan

Setiap kemas kini memori mendapat memory commit bernombor. Setiap commit merekod siapa yang menulisnya, bila ia berlaku, thread mana yang menulisnya, apa yang berubah, dan lokasi tepat untuk dibaca seterusnya.

## Pemasangan

Pasang skill daripada GitHub:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Di Windows, biasanya gunakan:

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Mulakan semula Codex selepas pemasangan.

## Mulakan Projek Baharu

Dalam projek baharu, minta Codex:

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

Atau jalankan skrip secara terus:

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

Ini akan mencipta `.codex-memory/` dan `AGENTS.md` jika perlu.

Secara lalai, ia tidak menimpa fail sedia ada.

## Sertai Projek Sedia Ada

Jika rakan pasukan anda sudah mempunyai `.codex-memory/`, minta Codex:

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

Atau jalankan:

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

Ini mengimbas memori sedia ada dan mencipta memory commit terindeks pertama jika belum ada.

## Gunakan Dengan Bahasa Semula Jadi

Anda tidak perlu menghafal semua arahan.

Mula bekerja:

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

Rekod kemajuan:

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

Sediakan handoff:

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

Padatkan memori panjang:

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

Import nota lama:

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## Arahan Terus

Sync thread ini:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

Selepas membaca lokasi memori yang dilaporkan, tandakan sebagai sudah dibaca:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

Commit memori thread:

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

Padatkan memori:

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

Semak status:

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## Cara Sync Bertambah Menjimatkan Konteks

SyncMind menulis setiap perubahan memori ke:

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

Setiap rekod mengandungi:

- nombor memori
- ID memori
- actor
- thread
- ringkasan
- fail memori yang berubah
- nombor entri dalam fail itu
- julat baris
- fail kod berkaitan

Jadi thread baharu hanya perlu membaca entri baharu yang tepat, bukan semua fail memori.

Contoh output sync:

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## Susun Atur Fail

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

## Keselamatan

SyncMind berhati-hati secara lalai.

- `init` mencipta fail yang hilang dan mengekalkan fail sedia ada
- `adopt` tidak pernah menimpa memori sedia ada
- `import` menyalin nota lama ke folder bertarikh masa
- `commit` menambah entri baharu
- `compact` mengarkibkan memori sebelum mengemas kini ringkasan
- penggantian yang merosakkan bukan sebahagian daripada aliran kerja biasa

## Kenapa Ini Wujud

Memori projek paling baik apabila ia boleh dilihat.

Fail mudah di-diff, disemak, di-commit, dipulihkan, dan dikongsi. SyncMind mengekalkan proses ini ringkas: tulis apa yang berubah, rekod di mana ia ditulis, dan biarkan thread seterusnya membaca hanya bahagian baharu.
