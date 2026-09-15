from __future__ import annotations

import argparse
import html
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, urlencode

PASS_CONCLUSIONS = {"success"}
FAIL_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}
VERIFIED = "VERIFIED"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"
SHIPPED = "SHIPPED"
NONE = "NONE"


def normalize_verification(conclusion: str | None) -> str:
    if conclusion in PASS_CONCLUSIONS:
        return VERIFIED
    if conclusion in FAIL_CONCLUSIONS:
        return FAIL
    return UNKNOWN


def _valid_timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return value


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


def _safe_get_json(get_json: Callable[[str], Any], path: str) -> Any | None:
    try:
        return get_json(path)
    except Exception:
        return None


def _unknown_verification(workflow: str) -> dict[str, Any]:
    return {
        "state": UNKNOWN,
        "workflow": workflow,
        "run_id": None,
        "url": "",
        "completed_at": None,
    }


def _workflow_evidence(repo: str, workflow: str, sha: str, get_json: Callable[[str], Any]) -> dict[str, Any]:
    query = urlencode({"head_sha": sha, "status": "completed", "per_page": 1})
    path = f"/repos/{repo}/actions/workflows/{quote(workflow, safe='')}/runs?{query}"
    payload = _safe_get_json(get_json, path)
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list) or not runs or not isinstance(runs[0], dict):
        return _unknown_verification(workflow)
    run = runs[0]
    completed_at = _valid_timestamp(run.get("updated_at"))
    if run.get("head_sha") != sha or completed_at is None:
        result = _unknown_verification(workflow)
        result["run_id"] = run.get("id")
        result["url"] = run.get("html_url") or ""
        return result
    return {
        "state": normalize_verification(run.get("conclusion")),
        "workflow": workflow,
        "run_id": run.get("id"),
        "url": run.get("html_url") or "",
        "completed_at": completed_at,
    }


def _collect_head(repo: str, get_json: Callable[[str], Any]) -> dict[str, Any]:
    repo_payload = _safe_get_json(get_json, f"/repos/{repo}")
    branch = repo_payload.get("default_branch") if isinstance(repo_payload, dict) else None
    if not isinstance(branch, str) or not branch:
        return {"branch": None, "sha": None}
    branch_payload = _safe_get_json(get_json, f"/repos/{repo}/branches/{quote(branch, safe='')}")
    commit = branch_payload.get("commit") if isinstance(branch_payload, dict) else None
    sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(sha, str) or len(sha) != 40:
        sha = None
    return {"branch": branch, "sha": sha}


def _collect_release(repo: str, workflow: str, head: dict[str, Any], head_verification: dict[str, Any], get_json: Callable[[str], Any]) -> tuple[str, dict[str, Any] | None]:
    payload = _safe_get_json(get_json, f"/repos/{repo}/releases?per_page=10")
    if not isinstance(payload, list):
        return UNKNOWN, None
    published: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            return UNKNOWN, None
        if item.get("draft", False):
            continue
        published_at = item.get("published_at")
        if published_at is None:
            continue
        if _valid_timestamp(published_at) is None:
            return UNKNOWN, None
        published.append(item)
    if not published:
        return NONE, None
    newest = max(published, key=lambda item: str(item["published_at"]))
    tag = newest.get("tag_name")
    release_sha = None
    if isinstance(tag, str) and tag:
        commit_payload = _safe_get_json(get_json, f"/repos/{repo}/commits/{quote(tag, safe='')}")
        if isinstance(commit_payload, dict):
            candidate = commit_payload.get("sha")
            if isinstance(candidate, str) and len(candidate) == 40:
                release_sha = candidate
    if release_sha and release_sha == head.get("sha"):
        release_verification = dict(head_verification)
    elif release_sha:
        release_verification = _workflow_evidence(repo, workflow, release_sha, get_json)
    else:
        release_verification = _unknown_verification(workflow)
    return SHIPPED, {
        "name": newest.get("name") or tag or "Unnamed release",
        "tag": tag or "",
        "published_at": newest["published_at"],
        "url": newest.get("html_url") or "",
        "sha": release_sha,
        "verification": release_verification,
    }


def _collect_project_snapshot(project: dict[str, Any], get_json: Callable[[str], Any]) -> dict[str, Any]:
    repo = project["repo"]
    workflow = project["workflow"]
    head = _collect_head(repo, get_json)
    verification = _workflow_evidence(repo, workflow, head["sha"], get_json) if head.get("sha") else _unknown_verification(workflow)
    release_state, release = _collect_release(repo, workflow, head, verification, get_json)
    return {"head": head, "verification": verification, "release_state": release_state, "release": release}


def collect_snapshot(config: dict[str, Any], get_json: Callable[[str], Any]) -> dict[str, Any]:
    validate_config(config)
    return {"projects": {project["key"]: _collect_project_snapshot(project, get_json) for project in config["projects"]}}


def latest_release(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    releases: list[dict[str, Any]] = []
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        return None
    for project in projects.values():
        if not isinstance(project, dict) or project.get("release_state") != SHIPPED:
            continue
        release = project.get("release")
        if isinstance(release, dict) and _valid_timestamp(release.get("published_at")) is not None:
            releases.append(release)
    if not releases:
        return None
    return max(releases, key=lambda release: str(release["published_at"]))


def _safe(value: Any) -> str:
    return html.escape(str(value), quote=False)


def _verification_color(state: str) -> str:
    return {VERIFIED: "#67e480", FAIL: "#ff5f56", UNKNOWN: "#9aa4b2"}.get(state, "#9aa4b2")


def _short_sha(value: Any) -> str:
    return str(value)[:7] if isinstance(value, str) and value else "unknown"


def _project_state_label(project_snapshot: dict[str, Any]) -> str:
    verification = project_snapshot.get("verification")
    state = verification.get("state") if isinstance(verification, dict) else UNKNOWN
    if state not in {VERIFIED, FAIL, UNKNOWN}:
        state = UNKNOWN
    return f"{state} · SHIPPED" if project_snapshot.get("release_state") == SHIPPED else state


def _release_verification_state(release: dict[str, Any] | None) -> str:
    if not isinstance(release, dict):
        return UNKNOWN
    verification = release.get("verification")
    if not isinstance(verification, dict):
        return UNKNOWN
    state = verification.get("state")
    return state if state in {VERIFIED, FAIL, UNKNOWN} else UNKNOWN


def render_svg(config: dict[str, Any], snapshot: dict[str, Any]) -> str:
    validate_config(config)
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        raise ValueError("snapshot projects must be an object")
    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="390" viewBox="0 0 1200 390" role="img" aria-labelledby="title desc">',
        '<title id="title">Current Signal</title>',
        '<desc id="desc">Current focus, product phase, exact-HEAD verification state, public release state, and GitHub Actions provenance.</desc>',
        '<rect width="1200" height="390" rx="18" fill="#0b0d10"/>',
        '<rect x="1" y="1" width="1198" height="388" rx="17" fill="none" stroke="#2b313a"/>',
        '<path d="M40 78H1160" stroke="#252a31" stroke-width="1"/>',
        '<text x="40" y="50" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="24" font-weight="700">CURRENT SIGNAL</text>',
        '<text x="40" y="106" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">FOCUS</text>',
        f'<text x="235" y="106" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18">{_safe(config["current_focus"])}</text>',
    ]
    y = 154
    for project in config["projects"]:
        key = project["key"]
        project_snapshot = projects.get(key, {})
        if not isinstance(project_snapshot, dict):
            project_snapshot = {}
        verification = project_snapshot.get("verification")
        if not isinstance(verification, dict):
            verification = {}
        state = verification.get("state")
        if state not in {VERIFIED, FAIL, UNKNOWN}:
            state = UNKNOWN
        label = _project_state_label(project_snapshot)
        head = project_snapshot.get("head") if isinstance(project_snapshot.get("head"), dict) else {}
        branch = head.get("branch")
        sha = head.get("sha")
        workflow = verification.get("workflow")
        provenance = f"{branch or 'unknown'}@{_short_sha(sha)} · {workflow or 'workflow unknown'}"
        svg.append(f'<circle cx="1125" cy="{y - 6}" r="6" fill="{_verification_color(state)}"/>')
        svg.append(f'<text x="40" y="{y}" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{_safe(key)}</text>')
        svg.append(f'<text x="235" y="{y}" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(project["status"])}</text>')
        svg.append(f'<text x="855" y="{y}" fill="#cbd3dd" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{_safe(label)}</text>')
        svg.append(f'<text x="235" y="{y + 23}" fill="#7f8a99" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13">{_safe(provenance)}</text>')
        y += 66
    release = latest_release(snapshot)
    latest_label = release["name"] if release else "No public release yet"
    release_state = _release_verification_state(release)
    svg.extend([
        '<path d="M40 298H1160" stroke="#252a31" stroke-width="1"/>',
        '<text x="40" y="332" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">LATEST SHIP</text>',
        f'<text x="235" y="332" fill="#ff6b4a" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(latest_label)} · {_safe(release_state)}</text>',
        '<text x="40" y="366" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">EVIDENCE</text>',
        '<text x="235" y="366" fill="#cbd3dd" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">exact-HEAD · GitHub Actions</text>',
        '</svg>',
    ])
    return "\n".join(svg) + "\n"


def atomic_write_text(target: Path, text: str, *, writer: Callable[[Path, str], None] | None = None) -> None:
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
            request = urllib.request.Request("https://api.github.com" + path, headers=headers)
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        snapshot = collect_snapshot(config, get_json)
    svg = render_svg(config, snapshot)
    atomic_write_text(Path(args.output), svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
