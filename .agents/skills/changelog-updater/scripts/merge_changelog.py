#!/usr/bin/env python3
"""Merge changelog entries into weekly changelog JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any


REQUIRED_ENTRY_KEYS = {"summary", "repo", "url"}


def monday_of_current_week(today: dt.date | None = None) -> str:
    current = today or dt.date.today()
    monday = current - dt.timedelta(days=current.weekday())
    return monday.isoformat()


def validate_entries(entries: Any) -> list[dict[str, str]]:
    if not isinstance(entries, list):
        raise ValueError("entries must be a JSON array")

    validated: list[dict[str, str]] = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {idx} must be an object")
        missing = REQUIRED_ENTRY_KEYS - set(entry)
        if missing:
            missing_display = ", ".join(sorted(missing))
            raise ValueError(f"entry {idx} missing required key(s): {missing_display}")

        summary = str(entry["summary"]).strip()
        repo = str(entry["repo"]).strip()
        url = str(entry["url"]).strip()

        if not summary or not repo or not url:
            raise ValueError(f"entry {idx} has empty summary/repo/url")

        validated.append({"summary": summary, "repo": repo, "url": url})

    return validated


def dedupe_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    seen_urls: set[str] = set()
    deduped: list[dict[str, str]] = []
    for entry in entries:
        url = entry["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(entry)
    return deduped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge summarized entries into data/changelog.json")
    parser.add_argument("--entries", required=True, help="Path to JSON array of entries")
    parser.add_argument("--changelog", default="data/changelog.json", help="Path to changelog file")
    parser.add_argument(
        "--week-of",
        default=monday_of_current_week(),
        help="ISO date for week bucket (defaults to current week's Monday)",
    )
    return parser.parse_args()


def load_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    args = parse_args()

    entries_path = pathlib.Path(args.entries)
    changelog_path = pathlib.Path(args.changelog)

    entries = validate_entries(load_json(entries_path))
    entries = dedupe_entries(entries)

    if not entries:
        print("No entries to merge")
        return 0

    changelog = load_json(changelog_path)
    weeks = changelog.setdefault("weeks", [])

    if not isinstance(weeks, list):
        raise ValueError("changelog 'weeks' field must be an array")

    existing_week = next((week for week in weeks if week.get("weekOf") == args.week_of), None)

    if existing_week is None:
        weeks.insert(0, {"weekOf": args.week_of, "entries": entries})
    else:
        existing_entries = existing_week.setdefault("entries", [])
        if not isinstance(existing_entries, list):
            raise ValueError("week 'entries' field must be an array")
        existing_week["entries"] = dedupe_entries(existing_entries + entries)

    with changelog_path.open("w", encoding="utf-8") as file:
        json.dump(changelog, file, indent=2)
        file.write("\n")

    print(f"Merged {len(entries)} entry(s) into week {args.week_of}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
