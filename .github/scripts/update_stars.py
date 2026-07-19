#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

OWNER = "YiShu5"
MARKER = re.compile(
    r"<!--stars:(?P<repo>[A-Za-z0-9_.-]+)-->(?P<value>[^<]*)<!--/stars-->"
)


def format_stars(count: int) -> str:
    if count < 1_000:
        return str(count)
    if count < 1_000_000:
        value = count / 1_000
        return f"{value:.1f}".removesuffix(".0") + "k"
    value = count / 1_000_000
    return f"{value:.1f}".removesuffix(".0") + "m"


def replace_markers(text: str, counts: dict[str, int]) -> str:
    def replacement(match: re.Match[str]) -> str:
        repo = match.group("repo")
        if repo not in counts:
            raise KeyError(f"Missing Star count for {repo}")
        return f"<!--stars:{repo}-->{format_stars(counts[repo])}<!--/stars-->"

    return MARKER.sub(replacement, text)


def fetch_stars(repo: str, token: str | None) -> int:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{repo}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "YiShu5-profile-star-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    return int(payload["stargazers_count"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh Star counts in Profile READMEs")
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    readmes = (repo_root / "README.md", repo_root / "README.zh-CN.md")
    texts = {path: path.read_text(encoding="utf-8") for path in readmes}
    repositories = sorted(
        {match.group("repo") for text in texts.values() for match in MARKER.finditer(text)}
    )
    if not repositories:
        raise RuntimeError("No Star markers found")

    token = os.environ.get("GITHUB_TOKEN")
    counts = {repo: fetch_stars(repo, token) for repo in repositories}
    changed = False
    for path, text in texts.items():
        updated = replace_markers(text, counts)
        if updated == text:
            continue
        changed = True
        print(f"update {path.name}")
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    if not changed:
        print("Star counts already current")
    elif args.dry_run:
        print("Dry run only; no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
