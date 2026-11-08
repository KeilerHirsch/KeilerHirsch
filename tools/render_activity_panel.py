#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

GRAPHQL_URL = "https://api.github.com/graphql"

WIDTH = 1200
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

# Curated profile statement. GitHub cannot infer personal experience from Linguist.
# Only change when the owner explicitly updates their working-language list.
WORKING_LANGUAGES = (
    "Ada/SPARK", "C", "C++", "C#", "Python", "Lua", "JavaScript",
    "TypeScript", "PowerShell", "Go", "Rust", "Kotlin", "Dart",
)
WEB_TECHNOLOGIES = ("HTML", "CSS")


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
) -> list[tuple[str, int, str]]:
    """Linguist languages from active nonempty original projects, not personal skills."""
    totals: dict[str, int] = defaultdict(int)
    colors: dict[str, str] = {}

    for repo in repositories:
        if repo["name"].casefold() == login.casefold() or repo.get("isArchived", False):
            continue
        if repo.get("isEmpty", False) or repo.get("isFork", False):
            continue
        for edge in repo.get("languages", {}).get("edges", []):
            name = edge["node"]["name"]
            totals[name] += int(edge["size"])
            color = edge["node"].get("color") or ""
            colors[name] = color if re.fullmatch(r"#[0-9a-fA-F]{6}", color) else FALLBACK

    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0].casefold()))
    return [(name, size, colors[name]) for name, size in ordered]


def total_language_bytes(repositories: list[dict], login: str) -> int:
    return sum(
        int(edge["size"])
        for repo in repositories
        if repo["name"].casefold() != login.casefold()
        and not repo.get("isArchived", False)
        and not repo.get("isEmpty", False)
        and not repo.get("isFork", False)
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
    best = f"best day {best_count} on {best_date:%Y-%m-%d}" if best_count else "no activity"
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
        and not repo.get("isEmpty", False)
        and not repo.get("isFork", False)
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
            f"Past 30 days: {thirty_total} contributions · "
            f"{thirty_active} active days · {thirty_best}"
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


def format_percentage(size: int, total: int) -> str:
    """Readable, honest labels for small language shares."""
    if not total:
        return "0%"
    percent = 100 * size / total
    if 0 < percent < 0.05:
        return "<0.1%"
    if percent < 10:
        return f"{percent:.1f}%"
    return f"{percent:.0f}%"


def render_svg(model: dict) -> str:
    languages = model["languages"]
    language_bytes = model["language_bytes"]
    months = model["months"]
    recent = model["recent"]

    legend_rows = max(1, (len(languages) + 2) // 3)
    legend_top = 227
    legend_bottom = legend_top + 29 * (legend_rows - 1)
    working_title_y = legend_bottom + 43
    working_first_y = working_title_y + 29
    working_second_y = working_first_y + 28
    web_tech_y = working_second_y + 28
    divider_after_languages = web_tech_y + 22
    activity_title_y = divider_after_languages + 36
    monthly_baseline = activity_title_y + 64
    monthly_date_y = monthly_baseline + 18
    activity_metrics_y = monthly_baseline + 40
    window_y = activity_metrics_y + 57
    portfolio_y = window_y + 55
    recent_title_y = portfolio_y + 51
    recent_top = recent_title_y + 29
    height = recent_top + 29 * max(len(recent), 1) + 39

    max_month = max((count for _, count in months), default=0) or 1
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
            f'viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">'
        ),
        '<title id="title">GitHub activity: code languages, contributions and portfolio</title>',
        (
            '<desc id="desc">GitHub Linguist shares from active, nonempty public original projects, '
            'excluding the profile repo, forks and archived projects. This is source-code composition, '
            'not a list of every language the developer knows. '
            'A separate static, owner-confirmed working-language list follows. '
            'GitHub contribution metrics and recently pushed nonempty projects follow.</desc>'
        ),
        f'<rect width="{WIDTH}" height="{height}" rx="18" fill="{BG}"/>',
        (
            f'<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" '
            f'rx="17" fill="none" stroke="{BORDER}"/>'
        ),
        svg_text(LEFT, 48, "GITHUB ACTIVITY", size=27, weight=700),
        svg_text(RIGHT, 27, "AUTO · GitHub GraphQL", fill=MUTED, size=14, anchor="end"),
        f'<path d="M{LEFT} 70H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, 107, model["account"], size=23, weight=600),
        f'<path d="M{LEFT} 133H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, 161, "LANGUAGES · ACTIVE ORIGINAL PROJECT CODE", size=17, weight=700),
        svg_text(
            RIGHT, 161,
            f"ALL {len(languages)} DETECTED · BYTE SHARE, NOT SKILL LEVEL",
            fill=MUTED, size=14, anchor="end",
        ),
        f'<rect x="{LEFT}" y="179" width="{TRACK_WIDTH}" height="15" rx="7" fill="{TRACK}"/>',
        (
            '<clipPath id="language-bar-clip">'
            f'<rect x="{LEFT}" y="179" width="{TRACK_WIDTH}" height="15" rx="7"/>'
            '</clipPath>'
        ),
        '<g clip-path="url(#language-bar-clip)">',
    ]

    cursor = float(LEFT)
    if language_bytes:
        for _, size, color in languages:
            width = TRACK_WIDTH * size / language_bytes
            parts.append(
                f'<rect x="{cursor:.3f}" y="179" width="{width:.3f}" '
                f'height="15" fill="{color}"/>'
            )
            cursor += width
    parts.append("</g>")

    if not languages:
        parts.append(
            svg_text(LEFT, legend_top, "No published original-repository source languages detected",
                     fill=SOFT, size=18)
        )
    else:
        columns = (LEFT, 422, 810)
        for i, (name, size, color) in enumerate(languages):
            x = columns[i % 3]
            y = legend_top + 29 * (i // 3)
            parts.append(
                f'<rect x="{x}" y="{y - 13}" width="12" height="12" '
                f'rx="3" fill="{color}"/>'
            )
            parts.append(
                svg_text(
                    x + 22, y, f"{name} {format_percentage(size, language_bytes)}",
                    fill=SOFT, size=17,
                )
            )

    parts += [
        svg_text(LEFT, working_title_y, "LANGUAGES I WORK WITH · OWNER-CONFIRMED", size=17, weight=700),
        svg_text(LEFT, working_first_y, " · ".join(WORKING_LANGUAGES[:7]), fill=SOFT, size=18),
        svg_text(LEFT, working_second_y, " · ".join(WORKING_LANGUAGES[7:]), fill=SOFT, size=18),
        svg_text(LEFT, web_tech_y, "Web technologies: " + " · ".join(WEB_TECHNOLOGIES),
                 fill=SOFT, size=17),
        f'<path d="M{LEFT} {divider_after_languages}H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, activity_title_y, "CONTRIBUTIONS · LAST 12 MONTHS", size=17, weight=700),
    ]

    start_x = LEFT
    bar_width = 25
    gap = 13
    for index, (month, count) in enumerate(months):
        bar_height = 5 if count == 0 else max(8, 38 * count / max_month)
        x = start_x + index * (bar_width + gap)
        y = monthly_baseline - bar_height
        parts.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
            f'height="{bar_height:.1f}" rx="3" fill="{ACCENT}"/>'
        )
        parts.append(svg_text(x + bar_width // 2, monthly_date_y, month[-2:],
                              fill=MUTED, size=13, anchor="middle"))

    parts += [
        svg_text(570, monthly_baseline - 14, model["contribution_totals"], fill=SOFT, size=18),
        f'<path d="M{LEFT} {activity_metrics_y + 18}H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, window_y, model["window"], size=21, weight=600),
        f'<path d="M{LEFT} {window_y + 19}H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, portfolio_y, model["portfolio"], fill=SOFT, size=20),
        f'<path d="M{LEFT} {portfolio_y + 19}H{RIGHT}" stroke="{TRACK}" stroke-width="1"/>',
        svg_text(LEFT, recent_title_y, "RECENTLY PUSHED ORIGINAL PROJECTS", size=17, weight=700),
    ]

    if recent:
        for i, repo in enumerate(recent):
            pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
            parts.append(
                svg_text(
                    LEFT, recent_top + 29 * i,
                    f"{short_repo_name(repo['name'])} · pushed {pushed:%Y-%m-%d}",
                    size=18,
                )
            )
    else:
        parts.append(svg_text(LEFT, recent_top, "No recent nonempty originals",
                              fill=SOFT, size=18))

    parts.append(
        svg_text(LEFT, height - 17,
                 "Linguist code-size shares; profile, archived, empty repos and forks excluded.",
                 fill=MUTED, size=14)
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
        isFork
        isEmpty
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
