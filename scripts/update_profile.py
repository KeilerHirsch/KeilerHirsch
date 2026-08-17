#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "KeilerHirsch"
PROFILE_REPO = f"{USER}/{USER}"
OWN_PREFIXES = (f"{USER}/", "KeilerHirsch-Labs/")
README = Path("README.md")

RECENT_START = "<!-- RECENT-WORK:START -->"
RECENT_END = "<!-- RECENT-WORK:END -->"
UPSTREAM_START = "<!-- OPEN-UPSTREAM:START -->"
UPSTREAM_END = "<!-- OPEN-UPSTREAM:END -->"
RELEASE_START = "<!-- LATEST-RELEASE:START -->"
RELEASE_END = "<!-- LATEST-RELEASE:END -->"

MAX_RECENT = 3
MAX_UPSTREAM = 4
RELEASE_REPOS = ("KeilerHirsch-Labs/schroedinger-sync",)


def github_json(url: str):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "KeilerHirsch-profile-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def event_date(event: dict) -> str:
    dt = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
    return dt.strftime("%d %b")


def iso_date(value: str) -> str:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.strftime("%d %b %Y")


def branch_from_ref(ref: str | None) -> str:
    if not ref:
        return "default branch"
    branch = ref.removeprefix("refs/heads/")
    return re.sub(r"[^A-Za-z0-9._/-]", "?", branch)


def clean_title(value: str) -> str:
    title = " ".join(value.split())
    return title.replace("[", "\\[").replace("]", "\\]")


def format_event(event: dict) -> str | None:
    event_type = event.get("type")
    repo = event.get("repo", {}).get("name")
    payload = event.get("payload", {})
    if not repo or repo == PROFILE_REPO:
        return None

    date = event_date(event)
    repo_url = f"https://github.com/{repo}"

    if event_type == "PushEvent":
        head = payload.get("head")
        branch = branch_from_ref(payload.get("ref"))
        url = f"{repo_url}/commit/{head}" if head else repo_url
        return f"- `{date}` — pushed to `{branch}` in [{repo}]({url})"

    if event_type == "IssueCommentEvent":
        issue = payload.get("issue", {})
        number = issue.get("number")
        url = issue.get("html_url")
        if number and url:
            kind = "PR" if issue.get("pull_request") else "issue"
            return f"- `{date}` — commented on {kind} [{repo}#{number}]({url})"

    if event_type == "IssuesEvent":
        issue = payload.get("issue", {})
        number = issue.get("number")
        url = issue.get("html_url")
        action = payload.get("action", "updated")
        if number and url:
            return f"- `{date}` — {action} issue [{repo}#{number}]({url})"

    if event_type == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        number = pr.get("number")
        url = pr.get("html_url")
        action = payload.get("action", "updated")
        if action == "closed" and pr.get("merged"):
            action = "merged"
        if number and url:
            return f"- `{date}` — {action} PR [{repo}#{number}]({url})"

    if event_type == "PullRequestReviewEvent":
        pr = payload.get("pull_request", {})
        number = pr.get("number")
        url = pr.get("html_url")
        if number and url:
            return f"- `{date}` — reviewed PR [{repo}#{number}]({url})"

    if event_type == "ReleaseEvent":
        release = payload.get("release", {})
        url = release.get("html_url", repo_url)
        action = payload.get("action", "published")
        return f"- `{date}` — {action} release in [{repo}]({url})"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        if ref_type in {"branch", "tag"} and ref:
            safe_ref = re.sub(r"[^A-Za-z0-9._/-]", "?", str(ref))
            return f"- `{date}` — created {ref_type} `{safe_ref}` in [{repo}]({repo_url})"

    return None


def recent_items() -> list[str]:
    events: list[dict] = []
    for page in (1, 2):
        batch = github_json(
            f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}"
        )
        if not batch:
            break
        events.extend(batch)

    candidates: list[tuple[str, str]] = []
    for event in events:
        rendered = format_event(event)
        if rendered:
            repo = event["repo"]["name"]
            candidates.append((repo, rendered))

    selected: list[str] = []
    seen_repos: set[str] = set()
    for repo, rendered in candidates:
        if repo in seen_repos:
            continue
        selected.append(rendered)
        seen_repos.add(repo)
        if len(selected) == MAX_RECENT:
            return selected

    for _, rendered in candidates:
        if rendered in selected:
            continue
        selected.append(rendered)
        if len(selected) == MAX_RECENT:
            break

    return selected


def open_upstream_items() -> list[str]:
    params = urllib.parse.urlencode(
        {
            "q": f"is:pr is:open author:{USER}",
            "sort": "updated",
            "order": "desc",
            "per_page": 100,
        }
    )
    data = github_json(f"https://api.github.com/search/issues?{params}")

    candidates: list[tuple[str, str]] = []
    for item in data.get("items", []):
        repo_url = item.get("repository_url", "")
        repo = repo_url.split("/repos/", 1)[-1]
        if not repo or repo.startswith(OWN_PREFIXES):
            continue

        number = item.get("number")
        url = item.get("html_url")
        title = clean_title(item.get("title", ""))
        if not number or not url or not title:
            continue

        rendered = f"- [{repo}#{number}]({url}) — {title}"
        candidates.append((repo, rendered))

    selected: list[str] = []
    seen_repos: set[str] = set()
    for repo, rendered in candidates:
        if repo in seen_repos:
            continue
        selected.append(rendered)
        seen_repos.add(repo)
        if len(selected) == MAX_UPSTREAM:
            return selected

    for _, rendered in candidates:
        if rendered in selected:
            continue
        selected.append(rendered)
        if len(selected) == MAX_UPSTREAM:
            break

    return selected


def latest_release_items() -> list[str]:
    lines: list[str] = []
    for repo in RELEASE_REPOS:
        release = github_json(f"https://api.github.com/repos/{repo}/releases/latest")
        tag = release.get("tag_name")
        url = release.get("html_url")
        published = release.get("published_at")
        assets = release.get("assets", [])
        if not tag or not url or not published:
            continue

        checksums = next((a for a in assets if a.get("name") == "SHA256SUMS"), None)
        verification = ""
        if checksums and checksums.get("browser_download_url"):
            verification = f" · [SHA256SUMS]({checksums['browser_download_url']})"

        lines.append(
            f"- [{repo} `{tag}`]({url}) — published {iso_date(published)}{verification}"
        )
    return lines


def replace_block(text: str, start: str, end: str, lines: list[str], label: str) -> str:
    if start not in text or end not in text:
        raise SystemExit(f"README {label} markers are missing; refusing to modify the file")
    if not lines:
        raise SystemExit(f"No {label} data found; refusing to erase current data")

    replacement = start + "\n" + "\n".join(lines) + "\n" + end
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Expected exactly one {label} block, replaced {count}")
    return updated


def main() -> None:
    text = README.read_text(encoding="utf-8")
    text = replace_block(
        text, RECENT_START, RECENT_END, recent_items(), "recent-work"
    )
    text = replace_block(
        text, UPSTREAM_START, UPSTREAM_END, open_upstream_items(), "open-upstream"
    )
    text = replace_block(
        text, RELEASE_START, RELEASE_END, latest_release_items(), "latest-release"
    )
    README.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
