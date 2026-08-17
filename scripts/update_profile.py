#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "KeilerHirsch"
PROFILE_REPO = f"{USER}/{USER}"
README = Path("README.md")
START = "<!-- RECENT-WORK:START -->"
END = "<!-- RECENT-WORK:END -->"
MAX_ITEMS = 3


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


def branch_from_ref(ref: str | None) -> str:
    if not ref:
        return "default branch"
    branch = ref.removeprefix("refs/heads/")
    return re.sub(r"[^A-Za-z0-9._/-]", "?", branch)


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
        if len(selected) == MAX_ITEMS:
            return selected

    for _, rendered in candidates:
        if rendered in selected:
            continue
        selected.append(rendered)
        if len(selected) == MAX_ITEMS:
            break

    return selected


def main() -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("README activity markers are missing; refusing to modify the file")

    items = recent_items()
    if not items:
        raise SystemExit("No supported public GitHub activity found; refusing to erase current data")

    replacement = START + "\n" + "\n".join(items) + "\n" + END
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Expected exactly one activity block, replaced {count}")

    README.write_text(updated, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
