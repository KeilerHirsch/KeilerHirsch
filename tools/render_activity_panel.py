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

WIDTH = 1200
HEIGHT = 540
LEFT = 40
RIGHT = 1160
TRACK_WIDTH = 1120

BG = "#0b0d10"
BORDER = "#2b313a"
MUTED = "#8e99a8"
TEXT = "#f4f7fa"
SOFT = "#cbd3dd"
TRACK = "#252a31"
FALLBACK = "#7f8a99"
ACCENT = "#67e480"
FONT = "ui-monospace, SFMono-Regular, Consolas, monospace"


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


def validated_repositories(user: dict) -> list[dict]:
    connection = user.get("originalRepos")
    if not isinstance(connection, dict):
        raise RuntimeError("GitHub repository data is missing")

    nodes = connection.get("nodes")
    total_count = connection.get("totalCount")
    if not isinstance(nodes, list) or not isinstance(total_count, int):
        raise RuntimeError("GitHub repository data is malformed")

    if len(nodes) != total_count:
        raise RuntimeError(
            f"GitHub repository query incomplete: received {len(nodes)} of {total_count} repositories"
        )
    return nodes


def language_breakdown(
    repositories: list[dict],
    login: str,
    limit: int = 4,
) -> list[tuple[str, int, str]]:
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


def total_language_bytes(repositories: list[dict], login: str) -> int:
    return sum(
        int(edge["size"])
        for repo in repositories
        if repo["name"].casefold() != login.casefold()
        and not repo.get("isArchived", False)
        for edge in repo.get("languages", {}).get("edges", [])
    )


def aggregate_months(days: list[dict], end: datetime) -> list[tuple[str, int]]:
    counts = defaultdict(int)
    for day in days:
        counts[day["date"][:7]] += int(day["contributionCount"])
    return [(key, counts[key]) for key in month_keys(end)]


def window_metrics(
    days: list[dict],
    now: datetime,
    window_days: int = 30,
) -> tuple[int, int, str]:
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


def recent_repositories(
    repositories: list[dict],
    login: str,
    limit: int = 3,
) -> list[dict]:
    candidates = [
        repo
        for repo in repositories
        if repo["name"].casefold() != login.casefold()
        and not repo.get("isArchived", False)
        and isinstance(repo.get("pushedAt"), str)
    ]
    return sorted(candidates, key=lambda repo: repo["pushedAt"], reverse=True)[:limit]


def short_repo_name(name: str, limit: int = 70) -> str:
    return name if len(name) <= limit else name[: limit - 1] + "…"


def contribution_days(contributions: dict) -> list[dict]:
    return [
        day
        for week in contributions["contributionCalendar"]["weeks"]
        for day in week["contributionDays"]
    ]


def build_panel_model(data: dict, now: datetime) -> dict:
    user = data["user"]
    repositories = validated_repositories(user)
    contributions = user["contributionsCollection"]
    days = contribution_days(contributions)
    languages = language_breakdown(repositories, user["login"])
    language_bytes = total_language_bytes(repositories, user["login"])
    months = aggregate_months(days, now)
    thirty_total, thirty_active, thirty_best = window_metrics(days, now, 30)

    stars = sum(int(repo.get("stargazerCount", 0)) for repo in repositories)
    downstream_forks = sum(int(repo.get("forkCount", 0)) for repo in repositories)
    fork_count = int(user["forkRepos"]["totalCount"])

    return {
        "account": (
            f"GitHub since {user['createdAt'][:4]} · "
            f"{user['publicRepos']['totalCount']} public repos · "
            f"{user['followers']['totalCount']} followers · "
            f"{user['following']['totalCount']} following"
        ),
        "languages": languages,
        "language_bytes": language_bytes,
        "months": months,
        "contribution_totals": (
            f"{contributions['contributionCalendar']['totalContributions']} contributions · "
            f"{contributions['totalCommitContributions']} commits · "
            f"{contributions['totalPullRequestContributions']} PRs"
        ),
        "window": (
            f"{thirty_total} contributions · {thirty_active} active days · {thirty_best}"
        ),
        "portfolio": (
            f"{user['publicRepos']['totalCount']} public · "
            f"{user['originalRepos']['totalCount']} original · "
            f"{fork_count} {'fork' if fork_count == 1 else 'forks'} · "
            f"{stars} {'star' if stars == 1 else 'stars'} · "
            f"{downstream_forks} downstream "
            f"{'fork' if downstream_forks == 1 else 'forks'}"
        ),
        "recent": recent_repositories(repositories, user["login"]),
    }


def svg_text(
    x: int,
    y: int,
    value: str,
    *,
    fill: str = TEXT,
    size: int = 19,
    weight: int | None = None,
    anchor: str | None = None,
) -> str:
    attributes = [
        f'x="{x}"',
        f'y="{y}"',
        f'fill="{fill}"',
        f'font-family="{FONT}"',
        f'font-size="{size}"',
    ]
    if weight is not None:
        attributes.append(f'font-weight="{weight}"')
    if anchor is not None:
        attributes.append(f'text-anchor="{anchor}"')
    return f"<text {' '.join(attributes)}>{html.escape(value)}</text>"


def render_svg(model: dict) -> str:
    months = model["months"]
    max_month = max((count for _, count in months), default=0) or 1

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">'
        ),
        '<title id="title">GitHub activity</title>',
        (
            '<desc id="desc">Automatically refreshed GitHub account metrics, language share, '
            'contribution momentum, portfolio totals, and recently pushed repositories.</desc>'
        ),
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="{BG}"/>',
        (
            f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" '
            f'rx="17" fill="none" stroke="{BORDER}"/>'
        ),
        svg_text(LEFT, 48, "GITHUB ACTIVITY", size=27, weight=700),
        svg_text(RIGHT, 24, "AUTO · GitHub GraphQL", fill=MUTED, size=13, anchor="end"),
        f'<path d="M{LEFT} 70H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, 108, model["account"], size=23, weight=600),
        f'<path d="M{LEFT} 132H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        f'<rect x="{LEFT}" y="148" width="{TRACK_WIDTH}" height="17" rx="8" fill="{TRACK}"/>',
    ]

    cursor = float(LEFT)
    legend = []
    language_bytes = model["language_bytes"]
    if language_bytes:
        for name, size, color in model["languages"]:
            width = TRACK_WIDTH * size / language_bytes
            parts.append(
                f'<rect x="{cursor:.1f}" y="148" width="{width:.1f}" '
                f'height="17" rx="8" fill="{color}"/>'
            )
            cursor += width
            legend.append(f"{name} {100 * size / language_bytes:.0f}%")

    parts += [
        svg_text(
            LEFT,
            198,
            " · ".join(legend) if legend else "No language data yet",
            fill=SOFT,
            size=20,
        ),
        f'<path d="M{LEFT} 219H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
    ]

    start_x = LEFT
    baseline = 276
    bar_width = 25
    gap = 13
    for index, (_, count) in enumerate(months):
        height = 5 if count == 0 else max(8, 40 * count / max_month)
        x = start_x + index * (bar_width + gap)
        y = baseline - height
        parts.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
            f'height="{height:.1f}" rx="3" fill="{ACCENT}"/>'
        )

    parts += [
        svg_text(570, 258, model["contribution_totals"], fill=SOFT, size=19),
        f'<path d="M{LEFT} 294H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, 334, model["window"], size=22, weight=600),
        f'<path d="M{LEFT} 358H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, 396, model["portfolio"], fill=SOFT, size=21),
        f'<path d="M{LEFT} 420H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
    ]

    recent = model["recent"]
    if recent:
        for y, repo in zip((458, 493, 526), recent):
            pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
            parts.append(
                svg_text(
                    LEFT,
                    y,
                    f"{short_repo_name(repo['name'])} · pushed {pushed:%Y-%m-%d}",
                    size=19,
                    weight=600,
                )
            )
    else:
        parts.append(
            svg_text(
                LEFT,
                458,
                "No recent public project activity",
                fill=SOFT,
                size=19,
            )
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
    parser.add_argument(
        "--user",
        default=os.environ.get("GITHUB_REPOSITORY_OWNER", "KeilerHirsch"),
    )
    parser.add_argument("--output", default="assets/activity-panel.svg")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    data = graphql(
        token,
        QUERY,
        {"login": args.user, "from": start.isoformat(), "to": now.isoformat()},
    )
    model = build_panel_model(data, now)
    Path(args.output).write_text(render_svg(model), encoding="utf-8")


if __name__ == "__main__":
    main()
