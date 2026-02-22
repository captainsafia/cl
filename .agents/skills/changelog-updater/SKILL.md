---
name: changelog-updater
description: Generate and maintain weekly natural-language changelog entries in data/changelog.json from recent GitHub commits. Use when asked to update the changelog, summarize latest commits, fetch weekly contributions, merge new weekly entries, or replace/avoid GitHub Actions-based changelog automation.
---

# Changelog Updater

## Overview

Use this skill to fetch recent commits, convert them into concise user-facing changelog entries, and merge them into `data/changelog.json`.

## Workflow

1. Fetch recent commits.
2. Summarize commits into 5-7 natural-language entries.
3. Merge entries into the correct `weekOf` bucket.
4. Optionally commit the updated changelog.

## Prerequisites

- Ensure GitHub CLI is installed: `gh`.
- Ensure GitHub CLI auth is valid: `gh auth status`.
- Run commands from repository root.

## Step 1: Fetch Recent Commits

Run:

```bash
.agents/skills/changelog-updater/scripts/fetch_commits.py --output /tmp/commits.json
```

Defaults:
- author: `captainsafia`
- org-scoped query: `dotnet`
- user-scoped query: `captainsafia`
- lookback window: 7 days

Override defaults when needed:

```bash
.agents/skills/changelog-updater/scripts/fetch_commits.py \
  --author <github-user> \
  --org <org-name> \
  --user <user-or-org> \
  --days <N> \
  --output /tmp/commits.json
```

If `/tmp/commits.json` is empty, stop and report that no new commits were found.

## Step 2: Produce Natural-Language Entries

Read `/tmp/commits.json` and create a JSON array with this exact shape:

```json
[
  {"summary": "Description of change", "repo": "owner/repo", "url": "https://..."}
]
```

Apply these rules:
- Generate at most 5-7 entries total.
- Consolidate related commits into single entries.
- Use concise user-friendly language.
- Avoid commit hashes and internal implementation detail.
- Emphasize impact or purpose.
- Preserve a valid commit URL per entry.

Write output to `/tmp/changelog-entries.json`.

## Step 3: Merge Entries into `data/changelog.json`

Run:

```bash
.agents/skills/changelog-updater/scripts/merge_changelog.py \
  --entries /tmp/changelog-entries.json \
  --changelog data/changelog.json
```

Behavior:
- Defaults `weekOf` to the Monday of the current week.
- Adds a new week at the top when missing.
- Appends to existing week when already present.
- Deduplicates entries by URL.

Override week explicitly when required:

```bash
.agents/skills/changelog-updater/scripts/merge_changelog.py \
  --entries /tmp/changelog-entries.json \
  --changelog data/changelog.json \
  --week-of YYYY-MM-DD
```

## Step 4: Optional Commit

Run when user asks to persist changes:

```bash
git add data/changelog.json
git commit -m "Update changelog for week of YYYY-MM-DD"
```

Compute `YYYY-MM-DD` as the same Monday used during merge.

## Output Contract

- Keep `data/changelog.json` as valid JSON.
- Keep top-level schema: `{ "weeks": [...] }`.
- Ensure each entry includes: `summary`, `repo`, `url`.
- Prefer one canonical entry per commit URL.
