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

SyncMind est un skill Codex qui garde la mémoire de projet synchronisée entre les personnes, les ordinateurs et les threads Codex.

Il ne cherche pas à faire retenir toute l'histoire à une seule conversation. Il place plutôt la mémoire de travail dans votre dépôt, enregistre chaque changement de mémoire, et permet à chaque nouveau thread de lire seulement ce qui a changé.

## Le Problème

Les threads Codex sont utiles, mais ils ne partagent pas la même mémoire active.

En équipe, cela devient vite gênant :

- le Codex d'une personne ne sait pas ce que le Codex d'une autre personne a déjà changé
- un nouveau thread ne voit pas les décisions de l'ancien thread
- les handoffs restent dans l'historique du chat au lieu du projet
- tout le monde relit trop de contexte juste pour trouver ce qui a changé
- les longs fichiers de mémoire finissent par gaspiller des tokens
- des notes existantes peuvent être écrasées par erreur par un script de configuration

SyncMind rend ces informations explicites et versionnées.

## Ce Que Ça Fait

SyncMind ajoute un dossier `.codex-memory/` à votre projet.

Dans ce dossier, il garde :

- le travail en cours et la propriété active des fichiers
- des fichiers de mémoire par thread
- des notes de handoff
- des journaux de tâches
- les décisions, les risques et les notes de déploiement
- un journal de commits mémoire lisible par machine
- un journal de commits mémoire lisible par humain
- des curseurs de synchronisation par thread
- des résumés compactés et des archives

Chaque mise à jour de mémoire reçoit un commit mémoire numéroté. Chaque commit indique qui l'a écrit, quand, depuis quel thread, ce qui a changé, et l'emplacement exact à lire ensuite.

## Installation

Installez le skill depuis GitHub :

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Sur Windows, la commande est généralement :

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Redémarrez Codex après l'installation.

## Commencer Un Nouveau Projet

Dans un nouveau projet, demandez à Codex :

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

Vous pouvez aussi exécuter le script directement :

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

Cela crée `.codex-memory/` et `AGENTS.md` si nécessaire.

Par défaut, les fichiers existants ne sont pas écrasés.

## Rejoindre Un Projet Existant

Si votre collègue a déjà un dossier `.codex-memory/`, demandez à Codex :

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

Ou exécutez :

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

Cela analyse la mémoire existante et crée un premier commit mémoire indexé s'il n'en existe pas encore.

## Utilisation En Langage Naturel

Vous n'avez pas besoin de mémoriser chaque commande.

Démarrer le travail :

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

Enregistrer l'avancement :

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

Préparer un handoff :

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

Compacter une longue mémoire :

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

Importer d'anciennes notes :

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## Commandes Directes

Synchroniser ce thread :

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

Après avoir lu les emplacements indiqués, marquez-les comme lus :

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

Créer un commit de mémoire de thread :

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

Compacter la mémoire :

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

Vérifier l'état :

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## Comment La Synchronisation Incrémentale Économise Le Contexte

SyncMind écrit chaque changement de mémoire dans :

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

Chaque enregistrement contient :

- numéro de mémoire
- id de mémoire
- acteur
- thread
- résumé
- fichier mémoire modifié
- numéro d'entrée dans ce fichier
- plage de lignes
- fichiers de code liés

Un nouveau thread peut donc lire seulement les nouvelles entrées exactes, au lieu de charger tous les fichiers de mémoire.

Exemple de sortie de synchronisation :

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## Structure Des Fichiers

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

## Sécurité

SyncMind est prudent par défaut.

- `init` crée les fichiers manquants et conserve les fichiers existants
- `adopt` n'écrase jamais la mémoire existante
- `import` copie les anciennes notes dans un dossier horodaté
- `commit` ajoute de nouvelles entrées
- `compact` archive la mémoire avant de mettre à jour le résumé
- le remplacement destructif ne fait pas partie du flux normal

## Pourquoi Ça Existe

La mémoire de projet fonctionne mieux quand elle est visible.

Les fichiers sont faciles à comparer, relire, committer, restaurer et partager. SyncMind garde le processus simple : écrire ce qui a changé, noter où cela a été écrit, et laisser le thread suivant lire seulement les nouvelles parties.
