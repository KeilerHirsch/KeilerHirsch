# Profile Command Center v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the KeilerHirsch GitHub profile into a professional builder-first landing page whose Current Signal is backed by exact-HEAD GitHub Actions evidence and public release provenance.

**Architecture:** Keep the profile self-contained in the existing public profile repository. `profile.json` remains the declarative source for human-owned focus/product phase, while `tools/render_profile_signal.py` derives verification and release evidence from GitHub's public REST API, fails closed on stale or malformed evidence, and renders one deterministic SVG consumed by `README.md`. The README explains the engineering identity, background and selected work without external vanity widgets or tracking services.

**Tech Stack:** Python 3 standard library, `unittest`, GitHub REST API, GitHub Actions, SVG, Markdown.

**Spec:** `docs/superpowers/specs/2026-09-15-profile-command-center-v2-design.md`

## Global Constraints

- Public identity is **builder-first**; security research / digital forensics / OSINT explain the engineering style rather than compete with it.
- Target density is **40% nerd / 60% professional landing page**.
- Keep the existing hero asset unless a separate redesign is explicitly approved.
- No badge soup, GitHub-stat slot machines, generic skill walls, terminal cosplay, external tracking, or third-party vanity-stat services.
- Product phase and verification evidence are separate concepts.
- `VERIFIED` requires the configured workflow to succeed for the **exact current default-branch HEAD SHA**.
- A successful workflow for an older SHA must never produce `VERIFIED`.
- Missing, malformed, ambiguous, inaccessible, or network-failed evidence must fail closed to `UNKNOWN`.
- A current-HEAD failed workflow must render `FAIL`; do not hide red states.
- `SHIPPED` requires a real public GitHub release and does not imply that the release commit is verified.
- `ATTESTED` is reserved for future real artifact/build provenance and is out of scope for this implementation.
- Ada/SPARK is presented as the primary high-assurance language without dogmatism or status-signaling.
- Public qualification wording must not imply an unearned title or degree.
- Heinze wording remains bounded to **13 of 24 full-time months completed; no qualification awarded**.
- Do not claim that the user's specific Heinze cohort was an Airbus cooperation course.
- `Feinwerkmechaniker` and `Elektroniker für Betriebstechnik` remain visible alongside clear English working translations.
- Bundeswehr wording is **23 months of voluntary military service in the German Armed Forces (Bundeswehr)**.
- Keep the personal README-source Easter egg stealth and harmless.
- Canonical public links only; no tracking parameters.
- Preserve existing atomic-write behavior and test-before-render workflow behavior.
- Work in an isolated worktree/branch at execution time; never rewrite history, force-push, or delete unrelated files.

---

## File map

- `README.md` — public landing page copy, section order, links, humor, Engineering DNA, stealth HTML-comment Easter egg.
- `profile.json` — human-owned focus, selected projects, product phase and configured workflow names; **no evidence state**.
- `tools/render_profile_signal.py` — GitHub API collection, exact-HEAD verification, release evidence normalization, deterministic SVG rendering.
- `tests/test_profile_signal.py` — evidence semantics, rendering, workflow contract, public fallback and README surface contract.
- `tests/fixtures/signal-snapshot.json` — deterministic normalized snapshot for offline rendering tests.
- `.github/workflows/profile-signal.yml` — scheduled/manual refresh, test gate, authenticated API access, conditional SVG commit.
- `assets/current-signal.svg` — generated public panel; never hand-edit.

---

### Task 1: Define the v2 evidence contract in tests

**Files:**
- Modify: `tests/test_profile_signal.py`
- Modify: `tests/fixtures/signal-snapshot.json`
- Read only: `profile.json`

**Interfaces:**
- Consumes: project records with `key`, `repo`, `status`, `workflow`.
- Produces this normalized project snapshot shape for later tasks:

```python
{
    "head": {"branch": "main", "sha": "a" * 40},
    "verification": {
        "state": "VERIFIED",  # VERIFIED | FAIL | UNKNOWN
        "workflow": "ci.yml",
        "run_id": 123,
        "url": "https://github.com/.../actions/runs/123",
        "completed_at": "2026-09-15T12:00:00Z",
    },
    "release_state": "NONE",  # SHIPPED | NONE | UNKNOWN
    "release": None,
}
```

A shipped release uses:

```python
{
    "release_state": "SHIPPED",
    "release": {
        "name": "PLLDN v0.0.1 Beta 1",
        "tag": "v0.0.1-beta.1",
        "published_at": "2026-09-07T17:21:54Z",
        "url": "https://github.com/.../releases/tag/v0.0.1-beta.1",
        "sha": "b" * 40,
        "verification": {
            "state": "VERIFIED",
            "workflow": "verify.yml",
            "run_id": 456,
            "url": "https://github.com/.../actions/runs/456",
            "completed_at": "2026-09-07T17:10:00Z",
        },
    },
}
```

- [ ] **Step 1: Replace the fixture with deterministic v2 evidence**

Write `tests/fixtures/signal-snapshot.json` exactly as:

```json
{
  "projects": {
    "WOLPERTINGER": {
      "head": {
        "branch": "main",
        "sha": "1111111111111111111111111111111111111111"
      },
      "verification": {
        "state": "VERIFIED",
        "workflow": "ci.yml",
        "run_id": 101,
        "url": "https://github.com/KeilerHirsch/WOLPERTINGER/actions/runs/101",
        "completed_at": "2026-09-15T12:00:00Z"
      },
      "release_state": "NONE",
      "release": null
    },
    "PLLDN": {
      "head": {
        "branch": "main",
        "sha": "2222222222222222222222222222222222222222"
      },
      "verification": {
        "state": "VERIFIED",
        "workflow": "verify.yml",
        "run_id": 202,
        "url": "https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/runs/202",
        "completed_at": "2026-09-15T12:05:00Z"
      },
      "release_state": "SHIPPED",
      "release": {
        "name": "PLLDN v0.0.1 Beta 1",
        "tag": "v0.0.1-beta.1",
        "published_at": "2026-09-07T17:21:54Z",
        "url": "https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/releases/tag/v0.0.1-beta.1",
        "sha": "2222222222222222222222222222222222222222",
        "verification": {
          "state": "VERIFIED",
          "workflow": "verify.yml",
          "run_id": 203,
          "url": "https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/runs/203",
          "completed_at": "2026-09-07T17:10:00Z"
        }
      }
    }
  }
}
```

- [ ] **Step 2: Add exact reusable test helpers**

At module scope add `urllib.error` and these helpers:

```python
import urllib.error


def single_project_config(
    *,
    repo="example/project",
    workflow="verify.yml",
    status="BUILDING",
):
    return {
        "current_focus": "Evidence contract test",
        "projects": [
            {
                "key": "PROJECT",
                "repo": repo,
                "status": status,
                "workflow": workflow,
            }
        ],
    }


def make_run(sha, conclusion="success", run_id=1):
    return {
        "id": run_id,
        "head_sha": sha,
        "conclusion": conclusion,
        "html_url": f"https://example.invalid/actions/runs/{run_id}",
        "updated_at": "2026-09-15T12:00:00Z",
    }


def route_json(routes):
    def get_json(path):
        if path not in routes:
            raise AssertionError(f"unexpected API path: {path}")
        value = routes[path]
        if isinstance(value, BaseException):
            raise value
        return value

    return get_json
```

Also correct the mojibake test focus in existing `setUp` methods to:

```python
"current_focus": "WOLPERTINGER — Presentation subsystem",
```

- [ ] **Step 3: Add concrete exact-HEAD success/stale/fail/missing/malformed tests**

Add to `ProfileSignalCollectionTests`:

```python
def test_collect_snapshot_verifies_exact_default_branch_head(self):
    config = single_project_config()
    head = "a" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": [make_run(head, "success", 11)]},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    project = snapshot["projects"]["PROJECT"]
    self.assertEqual(project["head"], {"branch": "main", "sha": head})
    self.assertEqual(project["verification"]["state"], "VERIFIED")


def test_stale_success_never_verifies_current_head(self):
    config = single_project_config()
    head = "a" * 40
    stale = "b" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": [make_run(stale, "success", 12)]},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    self.assertEqual(
        snapshot["projects"]["PROJECT"]["verification"]["state"],
        "UNKNOWN",
    )


def test_current_head_failure_maps_to_fail(self):
    config = single_project_config()
    head = "c" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": [make_run(head, "failure", 13)]},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    self.assertEqual(
        snapshot["projects"]["PROJECT"]["verification"]["state"],
        "FAIL",
    )


def test_missing_current_head_run_maps_to_unknown(self):
    config = single_project_config()
    head = "d" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": []},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    self.assertEqual(
        snapshot["projects"]["PROJECT"]["verification"]["state"],
        "UNKNOWN",
    )


def test_malformed_repo_payload_fails_closed(self):
    config = single_project_config()
    routes = {
        "/repos/example/project": {},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    project = snapshot["projects"]["PROJECT"]
    self.assertEqual(project["head"], {"branch": None, "sha": None})
    self.assertEqual(project["verification"]["state"], "UNKNOWN")
```

- [ ] **Step 4: Add concrete default-branch and release-binding tests**

Add:

```python
def test_default_branch_is_not_hardcoded_to_main(self):
    config = single_project_config()
    head = "e" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "develop"},
        "/repos/example/project/branches/develop": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": [make_run(head, "success", 14)]},
        "/repos/example/project/releases?per_page=10": [],
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    self.assertEqual(
        snapshot["projects"]["PROJECT"]["head"]["branch"],
        "develop",
    )


def test_public_release_is_shipped_and_binds_its_own_verification(self):
    config = single_project_config()
    head = "f" * 40
    release_sha = "1" * 40
    head_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    release_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={release_sha}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        head_path: {"workflow_runs": [make_run(head, "success", 15)]},
        "/repos/example/project/releases?per_page=10": [
            {
                "draft": False,
                "name": "Example v1",
                "tag_name": "v1.0.0",
                "published_at": "2026-09-10T12:00:00Z",
                "html_url": "https://example.invalid/releases/v1.0.0",
            }
        ],
        "/repos/example/project/commits/v1.0.0": {"sha": release_sha},
        release_path: {"workflow_runs": [make_run(release_sha, "success", 16)]},
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    project = snapshot["projects"]["PROJECT"]
    self.assertEqual(project["release_state"], "SHIPPED")
    self.assertEqual(project["release"]["sha"], release_sha)
    self.assertEqual(project["release"]["verification"]["state"], "VERIFIED")


def test_release_does_not_inherit_head_verification_for_different_sha(self):
    config = single_project_config()
    head = "2" * 40
    release_sha = "3" * 40
    head_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    release_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={release_sha}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        head_path: {"workflow_runs": [make_run(head, "success", 17)]},
        "/repos/example/project/releases?per_page=10": [
            {
                "draft": False,
                "name": "Example v1",
                "tag_name": "v1.0.0",
                "published_at": "2026-09-10T12:00:00Z",
                "html_url": "https://example.invalid/releases/v1.0.0",
            }
        ],
        "/repos/example/project/commits/v1.0.0": {"sha": release_sha},
        release_path: {"workflow_runs": []},
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    project = snapshot["projects"]["PROJECT"]
    self.assertEqual(project["verification"]["state"], "VERIFIED")
    self.assertEqual(project["release"]["verification"]["state"], "UNKNOWN")


def test_release_api_failure_is_unknown_not_shipped(self):
    config = single_project_config()
    head = "4" * 40
    workflow_path = (
        "/repos/example/project/actions/workflows/verify.yml/runs?"
        f"head_sha={head}&status=completed&per_page=1"
    )
    routes = {
        "/repos/example/project": {"default_branch": "main"},
        "/repos/example/project/branches/main": {"commit": {"sha": head}},
        workflow_path: {"workflow_runs": [make_run(head, "success", 18)]},
        "/repos/example/project/releases?per_page=10": urllib.error.URLError("boom"),
    }
    snapshot = self.renderer.collect_snapshot(config, route_json(routes))
    project = snapshot["projects"]["PROJECT"]
    self.assertEqual(project["release_state"], "UNKNOWN")
    self.assertIsNone(project["release"])
```

- [ ] **Step 5: Run the focused tests and confirm RED**

```bash
python -m unittest tests.test_profile_signal.ProfileSignalCollectionTests -v
```

Expected: failures because the current collector returns `ci` and does not collect exact default-branch HEAD evidence.

- [ ] **Step 6: Commit the test contract**

```bash
git add tests/test_profile_signal.py tests/fixtures/signal-snapshot.json
git commit -m "test: define profile evidence v2 contract"
```

---

### Task 2: Implement exact-HEAD and release evidence collection

**Files:**
- Modify: `tools/render_profile_signal.py`
- Modify: `tests/test_profile_signal.py`

**Interfaces:**
- Consumes: `profile.json` records and `get_json(path: str) -> Any`.
- Produces:
  - `normalize_verification(conclusion: str | None) -> str`
  - `_collect_head(repo: str, get_json: Callable[[str], Any]) -> dict[str, Any]`
  - `_workflow_evidence(repo: str, workflow: str, sha: str, get_json: Callable[[str], Any]) -> dict[str, Any]`
  - `_collect_release(...) -> tuple[str, dict[str, Any] | None]`
  - `_collect_project_snapshot(...) -> dict[str, Any]`
  - `collect_snapshot(...) -> dict[str, Any]`

- [ ] **Step 1: Replace CI vocabulary with verification vocabulary**

Replace `normalize_ci` with:

```python
VERIFIED = "VERIFIED"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"


def normalize_verification(conclusion: str | None) -> str:
    if conclusion in PASS_CONCLUSIONS:
        return VERIFIED
    if conclusion in FAIL_CONCLUSIONS:
        return FAIL
    return UNKNOWN
```

Update the existing normalization test to call `normalize_verification` and expect `VERIFIED`, `FAIL`, `UNKNOWN`.

- [ ] **Step 2: Add narrow network-failure handling and URL encoding**

Add imports:

```python
import urllib.error
from urllib.parse import quote, urlencode
```

Add:

```python
def _safe_get_json(get_json: Callable[[str], Any], path: str) -> Any | None:
    try:
        return get_json(path)
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return None
```

Do **not** catch `AssertionError`, `KeyError`, or all `Exception`; programming/test routing errors must stay visible.

- [ ] **Step 3: Implement exact workflow evidence**

Add:

```python
def _unknown_verification(workflow: str) -> dict[str, Any]:
    return {
        "state": UNKNOWN,
        "workflow": workflow,
        "run_id": None,
        "url": "",
        "completed_at": None,
    }


def _workflow_evidence(
    repo: str,
    workflow: str,
    sha: str,
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    query = urlencode({"head_sha": sha, "status": "completed", "per_page": 1})
    path = f"/repos/{repo}/actions/workflows/{quote(workflow, safe='')}/runs?{query}"
    payload = _safe_get_json(get_json, path)
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list) or not runs or not isinstance(runs[0], dict):
        return _unknown_verification(workflow)

    run = runs[0]
    if run.get("head_sha") != sha:
        evidence = _unknown_verification(workflow)
        evidence.update(
            run_id=run.get("id"),
            url=run.get("html_url") or "",
            completed_at=run.get("updated_at"),
        )
        return evidence

    return {
        "state": normalize_verification(run.get("conclusion")),
        "workflow": workflow,
        "run_id": run.get("id"),
        "url": run.get("html_url") or "",
        "completed_at": run.get("updated_at"),
    }
```

- [ ] **Step 4: Implement default-branch HEAD collection**

Add:

```python
def _collect_head(repo: str, get_json: Callable[[str], Any]) -> dict[str, Any]:
    repo_payload = _safe_get_json(get_json, f"/repos/{repo}")
    branch = repo_payload.get("default_branch") if isinstance(repo_payload, dict) else None
    if not isinstance(branch, str) or not branch:
        return {"branch": None, "sha": None}

    branch_payload = _safe_get_json(
        get_json,
        f"/repos/{repo}/branches/{quote(branch, safe='')}",
    )
    commit = branch_payload.get("commit") if isinstance(branch_payload, dict) else None
    sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(sha, str) or len(sha) < 7:
        sha = None
    return {"branch": branch, "sha": sha}
```

- [ ] **Step 5: Implement independent public-release evidence**

Add:

```python
def _collect_release(
    repo: str,
    workflow: str,
    head: dict[str, Any],
    head_verification: dict[str, Any],
    get_json: Callable[[str], Any],
) -> tuple[str, dict[str, Any] | None]:
    payload = _safe_get_json(get_json, f"/repos/{repo}/releases?per_page=10")
    if payload is None or not isinstance(payload, list):
        return "UNKNOWN", None

    published = [
        item
        for item in payload
        if isinstance(item, dict)
        and not item.get("draft", False)
        and item.get("published_at")
    ]
    if not published:
        return "NONE", None

    newest = max(published, key=lambda item: str(item["published_at"]))
    tag = newest.get("tag_name")
    release_sha = None
    if isinstance(tag, str) and tag:
        commit_payload = _safe_get_json(
            get_json,
            f"/repos/{repo}/commits/{quote(tag, safe='')}",
        )
        if isinstance(commit_payload, dict) and isinstance(commit_payload.get("sha"), str):
            release_sha = commit_payload["sha"]

    if release_sha and release_sha == head.get("sha"):
        release_verification = dict(head_verification)
    elif release_sha:
        release_verification = _workflow_evidence(repo, workflow, release_sha, get_json)
    else:
        release_verification = _unknown_verification(workflow)

    return "SHIPPED", {
        "name": newest.get("name") or tag or "Unnamed release",
        "tag": tag or "",
        "published_at": newest["published_at"],
        "url": newest.get("html_url") or "",
        "sha": release_sha,
        "verification": release_verification,
    }
```

- [ ] **Step 6: Replace `collect_snapshot` with v2 per-project collection**

Add:

```python
def _collect_project_snapshot(
    project: dict[str, Any],
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    repo = project["repo"]
    workflow = project["workflow"]
    head = _collect_head(repo, get_json)
    verification = (
        _workflow_evidence(repo, workflow, head["sha"], get_json)
        if head.get("sha")
        else _unknown_verification(workflow)
    )
    release_state, release = _collect_release(
        repo,
        workflow,
        head,
        verification,
        get_json,
    )
    return {
        "head": head,
        "verification": verification,
        "release_state": release_state,
        "release": release,
    }


def collect_snapshot(
    config: dict[str, Any],
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    validate_config(config)
    return {
        "projects": {
            project["key"]: _collect_project_snapshot(project, get_json)
            for project in config["projects"]
        }
    }
```

Delete the old `branch=main&status=completed&per_page=1` collector path entirely.

- [ ] **Step 7: Replace the authenticated live-mode fake with the exact v2 API surface**

Inside `test_main_live_mode_uses_github_token_and_api`, use:

```python
wolper_head = "a" * 40
plldn_head = "b" * 40


def fake_urlopen(request, timeout=0):
    self.assertEqual(request.headers.get("Authorization"), "Bearer test-token")
    url = request.full_url
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER"):
        return FakeResponse({"default_branch": "main"})
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER/branches/main"):
        return FakeResponse({"commit": {"sha": wolper_head}})
    if "/WOLPERTINGER/actions/workflows/ci.yml/runs?" in url:
        return FakeResponse({"workflow_runs": [make_run(wolper_head, "success", 31)]})
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER/releases?per_page=10"):
        return FakeResponse([])
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator"
    ):
        return FakeResponse({"default_branch": "main"})
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/branches/main"
    ):
        return FakeResponse({"commit": {"sha": plldn_head}})
    if "/PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/workflows/verify.yml/runs?" in url:
        return FakeResponse({"workflow_runs": [make_run(plldn_head, "success", 32)]})
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/releases?per_page=10"
    ):
        return FakeResponse([])
    raise AssertionError(url)
```

After running `main(...)`, assert:

```python
self.assertEqual(exit_code, 0)
svg = output_path.read_text(encoding="utf-8")
self.assertIn("VERIFIED", svg)
self.assertNotIn("CI PASS", svg)
```

- [ ] **Step 8: Replace the public unauthenticated fallback fake**

In `PublicApiFallbackTests`, use the same repository/branch routes but return empty workflow runs and releases, while asserting no Authorization header:

```python
def fake_urlopen(request, timeout=0):
    self.assertIsNone(request.headers.get("Authorization"))
    url = request.full_url
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER"):
        return FakeResponse({"default_branch": "main"})
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER/branches/main"):
        return FakeResponse({"commit": {"sha": "a" * 40}})
    if "/WOLPERTINGER/actions/workflows/ci.yml/runs?" in url:
        return FakeResponse({"workflow_runs": []})
    if url.endswith("/repos/KeilerHirsch/WOLPERTINGER/releases?per_page=10"):
        return FakeResponse([])
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator"
    ):
        return FakeResponse({"default_branch": "main"})
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/branches/main"
    ):
        return FakeResponse({"commit": {"sha": "b" * 40}})
    if "/PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/workflows/verify.yml/runs?" in url:
        return FakeResponse({"workflow_runs": []})
    if url.endswith(
        "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/releases?per_page=10"
    ):
        return FakeResponse([])
    raise AssertionError(url)
```

Assert the output contains `UNKNOWN` and no `CI PASS`.

- [ ] **Step 9: Run the collector/fallback suites and confirm GREEN**

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSignalCollectionTests \
  tests.test_profile_signal.PublicApiFallbackTests -v
```

Expected: all tests pass.

- [ ] **Step 10: Commit the collector**

```bash
git add tools/render_profile_signal.py tests/test_profile_signal.py
git commit -m "feat: bind profile verification to exact head"
```

---

### Task 3: Render Current Signal v2 with compact provenance

**Files:**
- Modify: `tools/render_profile_signal.py`
- Modify: `tests/test_profile_signal.py`

**Interfaces:**
- Consumes: normalized v2 snapshot from Task 2.
- Produces: deterministic `render_svg(config, snapshot) -> str` showing product phase, exact-HEAD verification, `SHIPPED`, short HEAD SHA and latest-release verification.

- [ ] **Step 1: Write concrete failing renderer tests**

Add `import copy` and update the deterministic render test:

```python
first = self.renderer.render_svg(self.config, self.snapshot)
second = self.renderer.render_svg(self.config, self.snapshot)
self.assertEqual(first, second)
ET.fromstring(first)
self.assertIn("CURRENT SIGNAL", first)
self.assertIn("WOLPERTINGER", first)
self.assertIn("BUILDING", first)
self.assertIn("VERIFIED", first)
self.assertIn("SHIPPED", first)
self.assertIn("main@1111111", first)
self.assertIn("PLLDN v0.0.1 Beta 1", first)
self.assertIn("exact-HEAD · GitHub Actions", first)
self.assertNotIn("CI PASS", first)
```

Add:

```python
def test_render_shows_fail_and_unknown_without_hiding_them(self):
    snapshot = copy.deepcopy(self.snapshot)
    snapshot["projects"]["WOLPERTINGER"]["verification"]["state"] = "FAIL"
    snapshot["projects"]["PLLDN"]["verification"]["state"] = "UNKNOWN"
    svg = self.renderer.render_svg(self.config, snapshot)
    ET.fromstring(svg)
    self.assertIn("FAIL", svg)
    self.assertIn("UNKNOWN · SHIPPED", svg)
```

Run:

```bash
python -m unittest tests.test_profile_signal.ProfileSignalTests -v
```

Expected: fail against the old `CI PASS` renderer.

- [ ] **Step 2: Add renderer helpers and v2 release selection**

Add:

```python
def _verification_color(state: str) -> str:
    return {
        VERIFIED: "#67e480",
        FAIL: "#ff5f56",
        UNKNOWN: "#9aa4b2",
    }.get(state, "#9aa4b2")


def _short_sha(value: Any) -> str:
    return value[:7] if isinstance(value, str) and value else "unknown"


def _project_state_label(project_snapshot: dict[str, Any]) -> str:
    verification = project_snapshot.get("verification")
    state = verification.get("state") if isinstance(verification, dict) else UNKNOWN
    if state not in {VERIFIED, FAIL, UNKNOWN}:
        state = UNKNOWN
    return (
        f"{state} · SHIPPED"
        if project_snapshot.get("release_state") == "SHIPPED"
        else state
    )


def latest_release(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    releases = []
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        return None
    for project in projects.values():
        if not isinstance(project, dict) or project.get("release_state") != "SHIPPED":
            continue
        release = project.get("release")
        if isinstance(release, dict) and release.get("published_at"):
            releases.append(release)
    if not releases:
        return None
    return max(releases, key=lambda item: str(item["published_at"]))
```

- [ ] **Step 3: Replace `render_svg` with the v2 command-center layout**

Use this implementation shape exactly; retain `_safe()` for every config/API-derived text value:

```python
def render_svg(config: dict[str, Any], snapshot: dict[str, Any]) -> str:
    validate_config(config)
    projects = snapshot.get("projects", {})
    if not isinstance(projects, dict):
        raise ValueError("snapshot projects must be an object")

    rows = []
    for project in config["projects"]:
        key = project["key"]
        project_snapshot = projects.get(key, {})
        if not isinstance(project_snapshot, dict):
            project_snapshot = {}
        head = project_snapshot.get("head", {})
        verification = project_snapshot.get("verification", {})
        if not isinstance(head, dict):
            head = {}
        if not isinstance(verification, dict):
            verification = {}
        state = verification.get("state")
        if state not in {VERIFIED, FAIL, UNKNOWN}:
            state = UNKNOWN
        provenance = (
            f"{head.get('branch') or 'unknown'}@{_short_sha(head.get('sha'))}"
            f" · {verification.get('workflow') or 'workflow unknown'}"
        )
        rows.append(
            (
                key,
                project["status"],
                _project_state_label(project_snapshot),
                provenance,
                state,
            )
        )

    release = latest_release(snapshot)
    latest_label = "No public release yet"
    release_state = UNKNOWN
    if release:
        latest_label = str(release.get("name") or release.get("tag") or "Unnamed release")
        release_verification = release.get("verification")
        if isinstance(release_verification, dict):
            candidate = release_verification.get("state")
            if candidate in {VERIFIED, FAIL, UNKNOWN}:
                release_state = candidate

    divider_y = 140 + len(rows) * 62
    latest_y = divider_y + 42
    evidence_y = divider_y + 84
    height = evidence_y + 30

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Current Signal</title>',
        '<desc id="desc">Current focus, product phase, exact-HEAD verification state, public release state, and GitHub Actions provenance.</desc>',
        f'<rect width="1200" height="{height}" rx="18" fill="#0b0d10"/>',
        f'<rect x="1" y="1" width="1198" height="{height - 2}" rx="17" fill="none" stroke="#2b313a"/>',
        '<path d="M40 78H1160" stroke="#252a31" stroke-width="1"/>',
        '<text x="40" y="50" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="24" font-weight="700">CURRENT SIGNAL</text>',
        '<text x="40" y="106" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">FOCUS</text>',
        f'<text x="235" y="106" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18">{_safe(config["current_focus"])}</text>',
    ]

    y = 154
    for key, product_status, state_label, provenance, state in rows:
        svg.extend(
            [
                f'<circle cx="1128" cy="{y - 6}" r="6" fill="{_verification_color(state)}"/>',
                f'<text x="40" y="{y}" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{_safe(key)}</text>',
                f'<text x="235" y="{y}" fill="#f4f7fa" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(product_status)}</text>',
                f'<text x="860" y="{y}" fill="#cbd3dd" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{_safe(state_label)}</text>',
                f'<text x="235" y="{y + 22}" fill="#7f8a99" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="13">{_safe(provenance)}</text>',
            ]
        )
        y += 62

    svg.extend(
        [
            f'<path d="M40 {divider_y}H1160" stroke="#252a31" stroke-width="1"/>',
            f'<text x="40" y="{latest_y}" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">LATEST SHIP</text>',
            f'<text x="235" y="{latest_y}" fill="#ff6b4a" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="18" font-weight="600">{_safe(latest_label)} · {_safe(release_state)}</text>',
            f'<text x="40" y="{evidence_y}" fill="#8e99a8" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">EVIDENCE</text>',
            f'<text x="235" y="{evidence_y}" fill="#cbd3dd" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">exact-HEAD · GitHub Actions</text>',
            '</svg>',
        ]
    )
    return "\n".join(svg) + "\n"
```

- [ ] **Step 4: Run renderer tests and a deterministic fixture render**

```bash
python -m unittest tests.test_profile_signal.ProfileSignalTests -v
python tools/render_profile_signal.py \
  --config profile.json \
  --snapshot tests/fixtures/signal-snapshot.json \
  --output /tmp/profile-signal-v2.svg
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
text = Path("/tmp/profile-signal-v2.svg").read_text(encoding="utf-8")
ET.fromstring(text)
assert "VERIFIED" in text
assert "SHIPPED" in text
assert "main@1111111" in text
assert "CI PASS" not in text
print("fixture SVG OK")
PY
```

Expected: tests pass and `fixture SVG OK` prints.

- [ ] **Step 5: Commit the renderer**

```bash
git add tools/render_profile_signal.py tests/test_profile_signal.py tests/fixtures/signal-snapshot.json
git commit -m "feat: render provenance-aware profile signal"
```

---

### Task 4: Rebuild the README as the 40%-nerd professional landing page

**Files:**
- Modify: `README.md`
- Modify: `tests/test_profile_signal.py`
- Keep unchanged: `assets/profile-hero.webp`

**Interfaces:**
- Consumes: existing hero and generated Current Signal SVG.
- Produces final order: `Hero -> Current Signal -> Selected Work -> How I Build -> Engineering DNA -> Security & Forensics -> MAYHEM Club -> Footer -> hidden source Easter egg`.

- [ ] **Step 1: Replace the old README contract with the v2 contract**

In `test_readme_contract`, retain hero-before-signal-before-selected-work and canonical-link checks, then enforce:

```python
required_sections = [
    "## Current signal",
    "## Selected work",
    "## How I build",
    "## Engineering DNA",
    "## Security & forensics",
    "## MAYHEM Club",
]
for section in required_sections:
    self.assertIn(section, readme)
positions = [readme.index(section) for section in required_sections]
self.assertEqual(positions, sorted(positions))

required_markers = [
    "Simple products. Uncomfortably serious engineering underneath.",
    "High-assurance software",
    "One core. Multiple presentation surfaces.",
    "Decisions you can defend.",
    "Evidence before claims.",
    "Over State of the Art by default.",
    "I would rather prove an invariant than explain later why",
    "Precision Mechanic",
    "Feinwerkmechaniker",
    "13 of 24 full-time months completed",
    "no qualification awarded",
    "Electronics Technician for Industrial Engineering",
    "Elektroniker für Betriebstechnik",
    "23 months of voluntary military service",
    "Autodidact by habit",
    "Polish",
    "German",
    "English",
    "GitHub is where the workshop became software",
    "Build cool shit. Share it. Get real feedback.",
    "Simple outside. Technically unpleasant to copy inside.",
    "The Man, The Myth, The Legend.",
]
for marker in required_markers:
    self.assertIn(marker, readme)

self.assertNotIn("Airbus", readme)
self.assertNotIn("utm_", readme.lower())
self.assertGreaterEqual(len(readme.split()), 350)
self.assertLessEqual(len(readme.split()), 650)

how_i_build = readme.split("## How I build", 1)[1].split("## Engineering DNA", 1)[0]
principles = [line for line in how_i_build.splitlines() if line.startswith("- **")]
self.assertEqual(len(principles), 4)
```

- [ ] **Step 2: Run the README contract and confirm RED**

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSurfaceContractTests.test_readme_contract -v
```

Expected: fail because the current README lacks the approved Engineering DNA and v2 hero/copy.

- [ ] **Step 3: Replace `README.md` with the approved concise narrative**

Write:

```markdown
<div align="center">

![KeilerHirsch — High-assurance inside. KISS outside.](assets/profile-hero.webp)

**Simple products. Uncomfortably serious engineering underneath.**

High-assurance software · security research · deterministic systems · reproducible evidence

[MyRank](https://myrank.dev/u/KeilerHirsch) · [MAYHEM Club](https://www.reddit.com/r/MAYHEMClub/) · [Ko-fi](https://ko-fi.com/keilerhirsch)

</div>

## Current signal

![Current engineering signal](assets/current-signal.svg)

The panel separates product phase from evidence. `VERIFIED` means the configured GitHub Actions workflow passed for the exact current default-branch HEAD; stale or ambiguous evidence stays `UNKNOWN`. `SHIPPED` means a real public release exists — not that verification is magically inherited.

## Selected work

### [WOLPERTINGER](https://github.com/KeilerHirsch/WOLPERTINGER)

**One core. Multiple presentation surfaces.**

An Elite Dangerous companion platform built around deterministic replay, provenance, explicit trust boundaries and a narrow high-assurance core. The complicated machinery belongs underneath; the Commander should not have to operate it.

### [PLLDN — Programming Language & Licensing Decision Navigator](https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator)

**Decisions you can defend.**

A deterministic language and licensing navigator where explicit project facts stay authoritative, unknown evidence stays unknown, and free text accelerates the workflow without becoming an oracle.

[Use PLLDN](https://keilerhirsch.github.io/PLLDN-Programming-Language-Licensing-Decision-Navigator/) · [Latest release](https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/releases)

## How I build

- **Evidence before claims.** Tests, provenance and reproducible artifacts should support what a README says.
- **Over State of the Art by default.** “Good enough” is a release decision, not an engineering philosophy.
- **Deterministic where it matters.** Core decisions should come from explicit rules and traceable facts whenever possible.
- **KISS outside. Assurance inside.** Complexity belongs behind the user-facing surface; critical boundaries get stronger assurance when the architecture benefits from it.

*If the UI looks simple, someone probably suffered in the architecture first.*

## Engineering DNA

**Ada/SPARK is my primary engineering language.** Not because obscurity is a personality trait, but because I do not like compromising at critical boundaries.

**I would rather prove an invariant than explain later why “that should never happen” happened.**

I still use C#, Python, JavaScript and whatever else fits the job. Not every component needs SPARK — but critical correctness is not where I like to negotiate.

I came to software from the physical world:

- **Precision Mechanic** (`Feinwerkmechaniker`) — completed German vocational qualification.
- **State-certified technician program in Mechanical Engineering — Aircraft Technology specialization** — Technische Fachschule Heinze, Hamburg; **13 of 24 full-time months completed; no qualification awarded**.
- **Electronics Technician for Industrial Engineering** (`Elektroniker für Betriebstechnik`) — completed German IHK vocational qualification.
- **23 months of voluntary military service** in the German Armed Forces (`Bundeswehr`).
- **Autodidact by habit** — largely self-taught in software engineering, security research, digital forensics, OSINT and systems work.

That background shaped how I approach software: tolerances, measurements, failure modes, maintainability and systems first — syntax second.

**GitHub is where the workshop became software — and the measurements stayed.**

**Languages:** Polish (native) · German (fluent / native-level) · English (very good)

*Formal education helped. So did a suspicious amount of self-teaching — and, apparently, 9th-grade Realschule Technik-AG.*

## Security & forensics

I approach systems with the same mindset I use to build them: preserve evidence, bind claims to sources, separate observation from inference, and make important state reproducible.

**Focus:** AI systems · agent tooling · digital forensics · OSINT · provenance

## MAYHEM Club

I am the **Founder & Mod** of [r/MAYHEMClub](https://www.reddit.com/r/MAYHEMClub/), a creator-first workshop for indie devs, modders, open-source builders and people shipping wonderfully weird things.

**Build cool shit. Share it. Get real feedback.**

---

**Simple outside. Technically unpleasant to copy inside. 😎**

<!--
🥚 You looked behind the curtain.

The Man, The Myth, The Legend.
— KeilerHirsch

The UI was the easy part.
-->
```

Do not add Airbus, private life context, employer claims, or additional qualifications.

- [ ] **Step 4: Run the surface contract and confirm GREEN**

```bash
python -m unittest tests.test_profile_signal.ProfileSurfaceContractTests -v
```

Expected: all surface-contract tests pass.

- [ ] **Step 5: Commit the landing page**

```bash
git add README.md tests/test_profile_signal.py
git commit -m "docs: rebuild profile command center"
```

---

### Task 5: Authenticate refresh and regenerate the public signal asset

**Files:**
- Modify: `.github/workflows/profile-signal.yml`
- Modify: `tests/test_profile_signal.py`
- Regenerate: `assets/current-signal.svg`

**Interfaces:**
- Consumes: renderer CLI.
- Produces: authenticated scheduled/manual GitHub API refresh while retaining the conditional SVG commit.

- [ ] **Step 1: Add a failing explicit-token workflow assertion**

In `test_workflow_contract`, add:

```python
self.assertIn("GITHUB_TOKEN: ${{ github.token }}", text)
```

Retain assertions for schedule, `workflow_dispatch`, `contents: write`, test execution, render command, diff check and conditional commit.

- [ ] **Step 2: Confirm RED**

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSurfaceContractTests.test_workflow_contract -v
```

Expected: fail because the render step does not currently export `github.token` as `GITHUB_TOKEN`.

- [ ] **Step 3: Wire the token only into the render step**

Change that step to:

```yaml
      - name: Render current signal
        id: signal
        env:
          GITHUB_TOKEN: ${{ github.token }}
        run: |
          python tools/render_profile_signal.py --config profile.json --output assets/current-signal.svg
          if git diff --quiet -- assets/current-signal.svg; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi
```

Do not widen permissions and do not add a new secret.

- [ ] **Step 4: Run the full suite**

```bash
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Generate the public SVG from live evidence**

```bash
python tools/render_profile_signal.py \
  --config profile.json \
  --output assets/current-signal.svg
```

Expected: exit code `0`; each project renders `VERIFIED`, `FAIL`, or `UNKNOWN`; exact-head provenance is present; `CI PASS` is absent. If `GITHUB_TOKEN` exists locally it is used; otherwise the tested public fallback is used. Never hand-edit the status.

- [ ] **Step 6: Validate the generated SVG and rerun tests**

```bash
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
text = Path("assets/current-signal.svg").read_text(encoding="utf-8")
ET.fromstring(text)
assert "CURRENT SIGNAL" in text
assert "exact-HEAD · GitHub Actions" in text
assert "CI PASS" not in text
print("SVG OK")
PY
python -m unittest discover -s tests -v
```

Expected: `SVG OK` and all tests pass.

- [ ] **Step 7: Commit workflow + generated asset**

```bash
git add .github/workflows/profile-signal.yml tests/test_profile_signal.py assets/current-signal.svg
git commit -m "ci: authenticate profile signal refresh"
```

---

### Task 6: Final audit and PR handoff

**Files:**
- Review: every file changed in Tasks 1–5
- No new production files expected

**Interfaces:**
- Consumes: complete implementation branch.
- Produces: one reviewable PR with verification evidence.

- [ ] **Step 1: Run deterministic verification**

```bash
python -m unittest discover -s tests -v
git diff --check
git status --short
```

Expected: all tests pass; `git diff --check` emits nothing; no unexpected working-tree changes.

- [ ] **Step 2: Run public-copy safety checks**

```bash
python - <<'PY'
from pathlib import Path
readme = Path("README.md").read_text(encoding="utf-8")
assert "Airbus" not in readme
assert "utm_" not in readme.lower()
assert "13 of 24 full-time months completed" in readme
assert "no qualification awarded" in readme
assert "23 months of voluntary military service" in readme
assert "The Man, The Myth, The Legend." in readme
assert "assets/profile-hero.webp" in readme
assert "assets/current-signal.svg" in readme
print("PUBLIC COPY OK")
PY
```

Expected: `PUBLIC COPY OK`.

- [ ] **Step 3: Inspect the complete branch diff**

```bash
git log --oneline --decorate --max-count=12
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- \
  README.md \
  profile.json \
  tools/render_profile_signal.py \
  tests/test_profile_signal.py \
  tests/fixtures/signal-snapshot.json \
  .github/workflows/profile-signal.yml \
  assets/current-signal.svg
```

Acceptance checks:

```text
profile.json contains product phase/focus only, never evidence state
collector has no latest-completed-main shortcut
README contains no Airbus course-level claim
README contains no private-life context or employer claim
README has no tracking parameters or external vanity widget
Easter egg exists only as an HTML source comment
current-signal.svg is generated, not hand-edited
```

- [ ] **Step 4: Confirm ancestry against current `origin/main`**

```bash
git fetch origin
git rev-parse origin/main
git merge-base --is-ancestor origin/main HEAD
```

Expected: ancestry check exits `0`. If `origin/main` advanced, stop and reconcile through the normal non-destructive workflow; never force-update history.

- [ ] **Step 5: Open the PR**

Title:

```text
docs: rebuild profile command center with exact-head evidence
```

Body:

```markdown
## Summary

- rebuilds the profile README around a builder-first high-assurance identity
- adds the approved Engineering DNA and public qualification wording
- upgrades Current Signal to exact-default-branch-HEAD workflow evidence
- separates VERIFIED, FAIL, UNKNOWN and SHIPPED semantics
- keeps the panel self-contained and tracking-free

## Verification

- `python -m unittest discover -s tests -v`
- `git diff --check`
- live `assets/current-signal.svg` render from GitHub public evidence
```

- [ ] **Step 6: Review the PR before merge**

The acceptance question is:

```text
Can a visitor understand within ~20–30 seconds what KeilerHirsch builds,
why the engineering is assurance-heavy, and which visible evidence supports it?
```

Do not merge if exact-HEAD semantics, qualification wording or public-safety boundaries are ambiguous.

---

## Self-review record

### Spec coverage

- Hero / builder-first identity: Task 4.
- Current Signal exact-HEAD semantics: Tasks 1–3.
- Fail-closed stale/malformed/network evidence: Tasks 1–2.
- Public releases + independent release verification: Tasks 1–3.
- Future ATTESTED intentionally excluded: Global Constraints.
- Selected Work WOLPERTINGER + PLLDN: Task 4.
- Four engineering principles + dry humor: Task 4.
- Ada/SPARK + invariant line: Task 4.
- Precision Mechanic / Heinze 13/24 / Electronics Technician / Bundeswehr / autodidact: Task 4.
- Languages: Task 4.
- Security & Forensics secondary to builder identity: Task 4.
- MAYHEM compact: Task 4.
- Stealth Easter egg: Task 4.
- Mobile-oriented compactness: Tasks 3–4.
- Explicit workflow authentication + test-before-render: Task 5.
- Public truthfulness / Airbus evidence boundary: Tasks 4 and 6.

### Placeholder scan

All behavioral steps contain concrete tests, implementation snippets, commands and expected outcomes. There are no `TBD`, `TODO`, “implement later”, empty test bodies, broad “add error handling” instructions, or references to undefined interfaces.

### Type / vocabulary consistency

- Verification state: `VERIFIED | FAIL | UNKNOWN`.
- Release state: `SHIPPED | NONE | UNKNOWN`.
- Product phase remains `project["status"]` from `profile.json` and never becomes evidence.
- Workflow filename remains `project["workflow"]`.
- Exact HEAD is `head.branch` + `head.sha`.
- Release verification is `release.verification` and is inherited from current HEAD only when release SHA exactly equals current HEAD SHA.
