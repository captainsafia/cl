#!/usr/bin/env python3
"""Fetch recent commits for changelog generation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from typing import Any
from urllib.parse import quote_plus


def run_gh_search(query: str) -> list[dict[str, Any]]:
    encoded_query = quote_plus(query)
    endpoint = (
        f"/search/commits?q={encoded_query}"
        "&sort=committer-date&order=desc&per_page=100"
    )
    command = [
        "gh",
        "api",
        endpoint,
        "--jq",
        '[.items[] | {date: .commit.committer.date[0:10], repo: .repository.full_name, message: (.commit.message | split("\\n")[0]), url: .html_url}]',
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"gh api failed for query '{query}': {stderr}")

    payload = result.stdout.strip() or "[]"
    data = json.loads(payload)
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected gh response for query '{query}'")

    return data


def dedupe_commits(commits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_urls: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for commit in commits:
        url = commit.get("url")
        if not isinstance(url, str) or not url:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(commit)
    return deduped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch recent commits for changelog summarization")
    parser.add_argument("--author", default="captainsafia", help="GitHub username for author filter")
    parser.add_argument("--org", default="dotnet", help="Organization for org-scoped query")
    parser.add_argument("--user", default="captainsafia", help="User/org scope for user-scoped query")
    parser.add_argument("--days", type=int, default=7, help="How many days back to search")
    parser.add_argument("--output", required=True, help="Path to write commit JSON array")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    cutoff = (dt.date.today() - dt.timedelta(days=args.days)).isoformat()
    query_org = f"author:{args.author} org:{args.org} committer-date:>{cutoff}"
    query_user = f"author:{args.author} user:{args.user} committer-date:>{cutoff}"

    try:
        commits_org = run_gh_search(query_org)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        commits_user = run_gh_search(query_user)
    except RuntimeError:
        commits_user = []

    commits = dedupe_commits(commits_org + commits_user)

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(commits, file, indent=2)
        file.write("\n")

    print(f"Fetched {len(commits)} commit(s) since {cutoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
