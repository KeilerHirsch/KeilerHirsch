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
        if repo["name"].casefold() == login.casefold():
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


def render_svg(data: dict, now: datetime) -> str:
    user = data["user"]
    contributions = user["contributionsCollection"]
    repositories = user["languageRepos"]["nodes"]
    languages = language_breakdown(repositories, user["login"])
    all_language_bytes = sum(
        int(edge["size"])
        for repo in repositories
        if repo["name"].casefold() != user["login"].casefold()
        for edge in repo.get("languages", {}).get("edges", [])
    )
    days = [
        day
        for week in contributions["contributionCalendar"]["weeks"]
        for day in week["contributionDays"]
    ]
    months = aggregate_months(days, now)
    max_month = max((count for _, count in months), default=0) or 1

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="210" viewBox="0 0 1200 210" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub activity</title>',
        '<desc id="desc">Compact GitHub account age, public repository and social counts, language share, and twelve-month public contribution activity.</desc>',
        f'<rect width="1200" height="210" rx="18" fill="{BG}"/>',
        f'<rect x="1" y="1" width="1198" height="208" rx="17" fill="none" stroke="{BORDER}"/>',
        f'<text x="40" y="48" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">ACTIVITY</text>',
        f'<text x="1160" y="22" text-anchor="end" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="11">updated {now:%Y-%m-%d} UTC</text>',
    ]
    metrics = (
        f"GitHub since {user['createdAt'][:4]} · {user['publicRepos']['totalCount']} repos · "
        f"{user['followers']['totalCount']} followers · {user['following']['totalCount']} following"
    )
    parts.append(
        f'<text x="200" y="48" fill="{TEXT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
        f'font-size="18" font-weight="600">{html.escape(metrics)}</text>'
    )

    parts += [
        f'<path d="M40 72H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="108" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">LANGUAGES</text>',
        f'<rect x="200" y="90" width="960" height="10" rx="5" fill="{TRACK}"/>',
    ]
    cursor = 200.0
    legend = []
    if all_language_bytes:
        for name, size, color in languages:
            width = 960 * size / all_language_bytes
            parts.append(f'<rect x="{cursor:.1f}" y="90" width="{width:.1f}" height="10" rx="5" fill="{color}"/>')
            cursor += width
            label = "Ada/SPARK" if name == "Ada" else name
            legend.append(f"{label} {100 * size / all_language_bytes:.0f}%")
    legend_text = " · ".join(legend) if legend else "No language data yet"
    parts.append(
        f'<text x="200" y="126" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
        f'font-size="14">{html.escape(legend_text)}</text>'
    )

    parts += [
        f'<path d="M40 145H1160" stroke="{TRACK}" stroke-width="1"/>',
        f'<text x="40" y="183" fill="{MUTED}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">12 MONTHS</text>',
    ]
    start_x = 200
    baseline = 190
    bar_width = 24
    gap = 14
    for index, (_, count) in enumerate(months):
        height = 4 if count == 0 else max(6, 34 * count / max_month)
        x = start_x + index * (bar_width + gap)
        y = baseline - height
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{height:.1f}" rx="3" fill="#67e480"/>')

    totals = (
        f"{contributions['contributionCalendar']['totalContributions']} contributions · "
        f"{contributions['totalCommitContributions']} commits · "
        f"{contributions['totalPullRequestContributions']} PRs"
    )
    parts.append(
        f'<text x="700" y="183" fill="{SOFT}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" '
        f'font-size="15">{html.escape(totals)}</text>'
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
    languageRepos: repositories(
      first: 100
      ownerAffiliations: [OWNER]
      privacy: PUBLIC
      isFork: false
      isArchived: false
    ) {
      nodes {
        name
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
