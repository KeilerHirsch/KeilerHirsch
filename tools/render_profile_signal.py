from __future__ import annotations

import argparse
import html
import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Callable


PASS_CONCLUSIONS = {"success"}
FAIL_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}


def normalize_ci(conclusion: str | None) -> str:
    if conclusion in PASS_CONCLUSIONS:
        return "PASS"
    if conclusion in FAIL_CONCLUSIONS:
        return "FAIL"
    return "UNKNOWN"


def validate_config(config: dict[str, Any]) -> None:
    focus = config.get("current_focus")
    projects = config.get("projects")
    if not isinstance(focus, str) or not focus.strip():
        raise ValueError("current_focus must be a non-empty string")
    if not isinstance(projects, list) or not projects:
        raise ValueError("projects must be a non-empty list")

    keys: list[str] = []
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError("each project must be an object")
        for field in ("key", "repo", "status", "workflow"):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise ValueError(f"project {field} must be a non-empty string")
        keys.append(project["key"])
    if len(keys) != len(set(keys)):
        raise ValueError("project keys must be unique")


def latest_release(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    releases: list[dict[str, Any]] = []
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        return None
    for project in projects.values():
        if isinstance(project, dict):
            release = project.get("release")
            if isinstance(release, dict) and release.get("published_at"):
                releases.append(release)
    if not releases:
        return None
    return max(releases, key=lambda release: str(release["published_at"]))


def _safe(value: Any) -> str:
    return html.escape(str(value), quote=False)


def _status_color(status: str) -> str:
    return {
        "PASS": "#67e480",
        "FAIL": "#ff5f56",
        "UNKNOWN": "#9aa4b2",
    }.get(status, "#9aa4b2")


def render_svg(config: dict[str, Any], snapshot: dict[str, Any]) -> str:
    validate_config(config)
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        raise ValueError("snapshot projects must be an object")
    rows: list[tuple[str, str, str]] = []
    for project in config["projects"]:
        key = project["key"]
        project_snapshot = projects.get(key, {})
        ci = "UNKNOWN"
        if isinstance(project_snapshot, dict):
            candidate = project_snapshot.get("ci")
            if isinstance(candidate, str) and candidate in {"PASS", "FAIL", "UNKNOWN"}:
                ci = candidate
        rows.append((key, project["status"], ci))

    release = latest_release(snapshot)
    latest_label = release["name"] if release else "No public release yet"

    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="330" viewBox="0 0 1200 330" role="img" aria-labelledby="title desc">',
        '<title id="title">Current Signal</title>',
        '<desc id="desc">Current engineering focus, project status, CI state, and latest shipped release.</desc>',
        '<rect width="1200" height="330" rx="18" fill="#0b0d10"/>',
        '<rect x="1" y="1" width="1198" height="328" rx="17" fill="none" stroke="#2b313a"/>',
        '<path d="M40 78H1160" stroke="#252a31" stroke-width="1"/>',
        '<text x="40" y="50" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="24" font-weight="700">CURRENT SIGNAL</text>',
        '<text x="40" y="106" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">FOCUS</text>',
        f'<text x="235" y="106" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18">{_safe(config["current_focus"])}</text>',
    ]

    y = 154
    for key, product_status, ci in rows:
        svg.append(f'<circle cx="1125" cy="{y - 6}" r="6" fill="{_status_color(ci)}"/>')
        svg.append(f'<text x="40" y="{y}" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{_safe(key)}</text>')
        svg.append(f'<text x="235" y="{y}" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(product_status)}</text>')
        svg.append(f'<text x="980" y="{y}" fill="#cbd3dd" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">CI {ci}</text>')
        y += 48

    svg.extend(
        [
            '<path d="M40 262H1160" stroke="#252a31" stroke-width="1"/>',
            '<text x="40" y="302" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">LATEST SHIP</text>',
            f'<text x="235" y="302" fill="#ff6b4a" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(latest_label)}</text>',
            '</svg>',
        ]
    )
    return "\n".join(svg) + "\n"


def atomic_write_text(
    target: Path,
    text: str,
    *,
    writer: Callable[[Path, str], None] | None = None,
) -> None:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    write = writer or (lambda path, value: path.write_text(value, encoding="utf-8", newline="\n"))
    try:
        write(temp, text)
        os.replace(temp, target)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise


def collect_snapshot(
    config: dict[str, Any],
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    validate_config(config)
    snapshot: dict[str, Any] = {"projects": {}}

    for project in config["projects"]:
        repo = project["repo"]
        workflow = project["workflow"]
        runs = get_json(
            f"/repos/{repo}/actions/workflows/{workflow}/runs?branch=main&status=completed&per_page=1"
        )
        workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
        conclusion = None
        if workflow_runs and isinstance(workflow_runs[0], dict):
            conclusion = workflow_runs[0].get("conclusion")

        releases_payload = get_json(f"/repos/{repo}/releases?per_page=10")
        releases = releases_payload if isinstance(releases_payload, list) else []
        published = [
            release
            for release in releases
            if isinstance(release, dict)
            and not release.get("draft", False)
            and release.get("published_at")
        ]
        newest = max(published, key=lambda item: str(item["published_at"])) if published else None

        release = None
        if newest:
            release = {
                "name": newest.get("name") or newest.get("tag_name") or "Unnamed release",
                "tag": newest.get("tag_name") or "",
                "published_at": newest["published_at"],
                "url": newest.get("html_url") or "",
            }

        snapshot["projects"][project["key"]] = {
            "ci": normalize_ci(conclusion),
            "release": release,
        }

    return snapshot


def _load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the KeilerHirsch profile Current Signal SVG.")
    parser.add_argument("--config", default="profile.json")
    parser.add_argument("--output", default="assets/current-signal.svg")
    parser.add_argument("--snapshot")
    args = parser.parse_args(argv)

    config = _load_json(Path(args.config))
    validate_config(config)
    if args.snapshot:
        snapshot = _load_json(Path(args.snapshot))
    else:
        token = os.environ.get("GITHUB_TOKEN")

        def get_json(path: str) -> Any:
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "KeilerHirsch-profile-signal",
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            request = urllib.request.Request(
                "https://api.github.com" + path,
                headers=headers,
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))

        snapshot = collect_snapshot(config, get_json)

    svg = render_svg(config, snapshot)
    atomic_write_text(Path(args.output), svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
