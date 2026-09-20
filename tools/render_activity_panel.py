#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

GRAPHQL_URL = "https://api.github.com/graphql"
BG = "#0b0d10"
BORDER = "#2b313a"
MUTED = "#8e99a8"
TEXT = "#f4f7fa"
SOFT = "#cbd3dd"
TRACK = "#252a31"
FALLBACK = "#7f8a99"
ACCENT = "#67e480"


def graphql(token: str, query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    request = Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "KeilerHirsch-profile-activity",
        },
    )
    with urlopen(request, timeout=20) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]


def month_keys(end: datetime, count: int = 12) -> list[str]:
    index = end.year * 12 + (end.month - 1)
    result = []
    for offset in reversed(range(count)):
        value = index - offset
        result.append(f"{value // 12:04d}-{value % 12 + 1:02d}")
    return result


def language_breakdown(repositories: list[dict], login: str, limit: int = 4) -> list[tuple[str, int, str]]:
    totals: dict[str, int] = defaultdict(int)
    colors: dict[str, str] = {}
    for repo in repositories:
        if repo["name"].casefold() == login.casefold() or repo.get("isArchived", False):
            continue
        for edge in repo.get("languages", {}).get("edges", []):
            name = edge["node"]["name"]
            totals[name] += int(edge["size"])
            colors[name] = edge["node"].get("color") or FALLBACK
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0].casefold()))
    return [(name, size, colors[name]) for name, size in ordered[:limit]]


def aggregate_months(days: list[dict], end: datetime) -> list[tuple[str, int]]:
    counts = defaultdict(int)
    for day in days:
        counts[day["date"][:7]] += int(day["contributionCount"])
    return [(key, counts[key]) for key in month_keys(end)]


def window_metrics(days: list[dict], now: datetime, window_days: int = 30) -> tuple[int, int, str]:
    cutoff = (now - timedelta(days=window_days - 1)).date()
    selected = []
    for day in days:
        date = datetime.fromisoformat(day["date"]).date()
        if cutoff <= date <= now.date():
            selected.append((date, int(day["contributionCount"])))
    total = sum(count for _, count in selected)
    active = sum(1 for _, count in selected if count > 0)
    if not selected:
        return 0, 0, "no activity"
    best_date, best_count = max(selected, key=lambda item: (item[1], item[0]))
    best = f"best day {best_count} on {best_date:%m-%d}" if best_count else "best day 0"
    return total, active, best


def recent_repositories(repositories: list[dict], login: str, limit: int = 3) -> list[dict]:
    candidates = [
        repo
        for repo in repositories
        if repo["name"].casefold() != login.casefold()
        and not repo.get("isArchived", False)
        and isinstance(repo.get("pushedAt"), str)
    ]
    return sorted(candidates, key=lambda repo: repo["pushedAt"], reverse=True)[:limit]


def short_repo_name(name: str, limit: int = 38) -> str:
    return name if len(name) <= limit else name[: limit - 1] + "…"


def render_svg(data: dict, now: datetime) -> str:
    user = data["user"]
    contributions = user["contributionsCollection"]
    repositories = user["originalRepos"]["nodes"]
    languages = language_breakdown(repositories, user["login"])
    all_language_bytes = sum(
        int(edge["size"])
        for repo in repositories
        if repo["name"].casefold() != user["login"].casefold() and not repo.get("isArchived", False)
        for edge in repo.get("languages", {}).get("edges", [])
    )
    days = [
        day
        for week in contributions["contributionCalendar"]["weeks"]
        for day in week["contributionDays"]
    ]
    months = aggregate_months(days, now)
    max_month = max((count for _, count in months), default=0) or 1
    thirty_total, thirty_active, thirty_best = window_metrics(days, now, 30)
    recent = recent_repositories(repositories, user["login"])

    original_count = int(user["originalRepos"]["totalCount"])
    fork_count = int(user["forkRepos"]["totalCount"])
    total_stars = sum(int(repo.get("stargazerCount", 0)) for repo in repositories)
    downstream_forks = sum(int(repo.get("forkCount", 0)) for repo in repositories)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="540" viewBox="0 0 1200 540" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub activity</title>',
        '<desc id="desc">Live GitHub account metrics, language share, contribution momentum, portfolio totals, and recently pushed repositories.</desc>',
        f'<rect width="1200" height="540" rx="18" fill="{BG}"/>',
        f'<rect x="1" y="1" width="1198" height="538" rx="17" fill="none" stroke="{BORDER}"/>',
        f'<text x="40" y="48" fill="{TEXT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="27" font-weight="700">GITHUB ACTIVITY</text>',
        f'<text x="1160" y="24" text-anchor="end" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13">updated {now:%Y-%m-%d %H:%M} UTC</text>',
        f'<path d="M40 70H1160" stroke="{TRACK}" stroke-width="1"/>',
    ]

    account = (
        f"GitHub since {user['createdAt'][:4]} · {user['publicRepos']['totalCount']} public repos · "
        f"{user['followers']['totalCount']} followers · {user['following']['totalCount']} following"
    )
    parts += [
        f'<text x="40" y="108" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">ACCOUNT</text>',
        f'<text x="220" y="108" fill="{TEXT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="21" font-weight="600">{html.escape(account)}</text>',
        f'<path d="M40 132H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="171" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">LANGUAGES</text>',
        f'<rect x="220" y="148" width="940" height="15" rx="7" fill="{TRACK}"/>',
    ]

    cursor = 220.0
    legend = []
    if all_language_bytes:
        for name, size, color in languages:
            width = 940 * size / all_language_bytes
            parts.append(f'<rect x="{cursor:.1f}" y="148" width="{width:.1f}" height="15" rx="7" fill="{color}"/>')
            cursor += width
            label = "Ada/SPARK" if name == "Ada" else name
            legend.append(f"{label} {100 * size / all_language_bytes:.0f}%")
    legend_text = " · ".join(legend) if legend else "No language data yet"
    parts += [
        f'<text x="220" y="198" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18">{html.escape(legend_text)}</text>',
        f'<path d="M40 219H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="258" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">12 MONTHS</text>',
    ]

    start_x = 220
    baseline = 276
    bar_width = 25
    gap = 13
    for index, (_, count) in enumerate(months):
        height = 5 if count == 0 else max(8, 40 * count / max_month)
        x = start_x + index * (bar_width + gap)
        y = baseline - height
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{height:.1f}" rx="3" fill="{ACCENT}"/>')

    totals = (
        f"{contributions['contributionCalendar']['totalContributions']} contributions · "
        f"{contributions['totalCommitContributions']} commits · "
        f"{contributions['totalPullRequestContributions']} PRs"
    )
    parts += [
        f'<text x="710" y="258" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">{html.escape(totals)}</text>',
        f'<path d="M40 294H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="334" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">30 DAYS</text>',
        f'<text x="220" y="334" fill="{TEXT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="20" font-weight="600">{thirty_total} contributions · {thirty_active} active days · {html.escape(thirty_best)}</text>',
        f'<path d="M40 358H1160" stroke="{TRACK}" stroke-width="1"/>',
    ]

    portfolio = (
        f"{user['publicRepos']['totalCount']} public · {original_count} original · "
        f"{fork_count} {'fork' if fork_count == 1 else 'forks'} · "
        f"{total_stars} {'star' if total_stars == 1 else 'stars'} · "
        f"{downstream_forks} downstream {'fork' if downstream_forks == 1 else 'forks'}"
    )
    parts += [
        f'<text x="40" y="396" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">PORTFOLIO</text>',
        f'<text x="220" y="396" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="19">{html.escape(portfolio)}</text>',
        f'<path d="M40 420H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="458" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">RECENT WORK</text>',
    ]

    if recent:
        row_y = [458, 493, 526]
        for y, repo in zip(row_y, recent):
            pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
            label = f"{short_repo_name(repo['name'])} · pushed {pushed:%Y-%m-%d}"
            parts.append(
                f'<text x="220" y="{y}" fill="{TEXT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
                f'font-size="17" font-weight="600">{html.escape(label)}</text>'
            )
    else:
        parts.append(
            f'<text x="220" y="458" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="17">No recent public project activity</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    createdAt
    followers { totalCount }
    following { totalCount }
    publicRepos: repositories(ownerAffiliations: [OWNER], privacy: PUBLIC) { totalCount }
    forkRepos: repositories(ownerAffiliations: [OWNER], privacy: PUBLIC, isFork: true) { totalCount }
    originalRepos: repositories(
      first: 100
      ownerAffiliations: [OWNER]
      privacy: PUBLIC
      isFork: false
      orderBy: {field: PUSHED_AT, direction: DESC}
    ) {
      totalCount
      nodes {
        name
        isArchived
        pushedAt
        stargazerCount
        forkCount
        languages(first: 100) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "KeilerHirsch"))
    parser.add_argument("--output", default="assets/activity-panel.svg")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    data = graphql(token, QUERY, {"login": args.user, "from": start.isoformat(), "to": now.isoformat()})
    Path(args.output).write_text(render_svg(data, now), encoding="utf-8")


if __name__ == "__main__":
    main()
