# Profile Command Center v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the KeilerHirsch GitHub profile into a professional builder-first landing page whose Current Signal is backed by exact-HEAD GitHub Actions evidence and public release provenance.

**Architecture:** Keep the profile self-contained in the existing public profile repository. `profile.json` remains the declarative source for human-owned product phase/focus, while `tools/render_profile_signal.py` derives verification and release evidence from GitHub's public REST API, fails closed on stale or malformed evidence, and renders one deterministic SVG consumed by `README.md`. The README then explains the engineering identity, background and selected work without adding external vanity widgets or tracking services.

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
- Missing, malformed, ambiguous, or inaccessible evidence must fail closed to `UNKNOWN`.
- A current-HEAD failed workflow must render `FAIL`; do not hide red states.
- `SHIPPED` requires a real public GitHub release and does not imply that the release commit is verified.
- `ATTESTED` is reserved for future real artifact/build provenance and is out of scope for this implementation.
- Ada/SPARK is presented as the primary high-assurance language without dogmatism or status-signaling.
- Public qualification wording must not imply an unearned title or degree.
- Heinze wording must remain bounded to **13 of 24 full-time months completed; no qualification awarded**.
- Do not claim that the user's specific Heinze cohort was an Airbus cooperation course.
- `Feinwerkmechaniker` and `Elektroniker für Betriebstechnik` remain visible alongside clear English working translations.
- Bundeswehr wording is **23 months of voluntary military service in the German Armed Forces (Bundeswehr)**.
- Keep the personal README-source Easter egg stealth and harmless.
- Canonical public links only; no tracking parameters.
- Preserve the existing atomic-write behavior and the existing test-before-render workflow shape.
- Work in an isolated worktree/branch at execution time; do not rewrite history, force-push, or delete unrelated files.

---

## File map

- `README.md` — public landing page copy, section order, links, humor, Engineering DNA and stealth HTML-comment Easter egg.
- `profile.json` — human-owned current focus, selected projects, product phase and configured workflow names. No evidence state is stored here.
- `tools/render_profile_signal.py` — GitHub API collection, exact-HEAD verification semantics, release evidence normalization and deterministic SVG rendering.
- `tests/test_profile_signal.py` — unit tests for evidence semantics, rendering, workflow contract and README surface contract.
- `tests/fixtures/signal-snapshot.json` — deterministic normalized snapshot used for offline rendering tests.
- `.github/workflows/profile-signal.yml` — scheduled/manual refresh, test gate, authenticated GitHub API access and conditional SVG commit.
- `assets/current-signal.svg` — generated public panel; never hand-edit.

---

### Task 1: Lock the normalized evidence contract with failing tests

**Files:**
- Modify: `tests/test_profile_signal.py`
- Modify: `tests/fixtures/signal-snapshot.json`
- Read only: `profile.json`

**Interfaces:**
- Consumes: current `profile.json` project records with `key`, `repo`, `status`, `workflow`.
- Produces: normalized per-project snapshot shape used by all later tasks:

```python
{
    "head": {
        "branch": "main",
        "sha": "1111111111111111111111111111111111111111",
    },
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

For a shipped release:

```python
{
    "release_state": "SHIPPED",
    "release": {
        "name": "PLLDN v0.0.1 Beta 1",
        "tag": "v0.0.1-beta.1",
        "published_at": "2026-09-07T17:21:54Z",
        "url": "https://github.com/.../releases/tag/v0.0.1-beta.1",
        "sha": "2222222222222222222222222222222222222222",
        "verification": {
            "state": "VERIFIED",
            "workflow": "verify.yml",
            "run_id": 456,
            "url": "https://github.com/.../actions/runs/456",
            "completed_at": "2026-09-07T17:00:00Z",
        },
    },
}
```

- [ ] **Step 1: Replace the fixture with the v2 normalized evidence shape**

Use exact deterministic values so rendering never depends on the network:

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

- [ ] **Step 2: Add failing exact-HEAD collection tests**

Add helpers inside `ProfileSignalCollectionTests` so each test controls the fake API precisely:

```python
def make_repo_payload(default_branch="main"):
    return {"default_branch": default_branch}


def make_branch_payload(sha):
    return {"commit": {"sha": sha}}


def make_run(sha, conclusion="success", run_id=1):
    return {
        "id": run_id,
        "head_sha": sha,
        "conclusion": conclusion,
        "html_url": f"https://example.invalid/actions/runs/{run_id}",
        "updated_at": "2026-09-15T12:00:00Z",
    }
```

Add these tests with concrete assertions:

```python
def test_collect_snapshot_verifies_exact_default_branch_head(self):
    head = "a" * 40

    def get_json(path):
        if path == "/repos/KeilerHirsch/WOLPERTINGER":
            return make_repo_payload("main")
        if path == "/repos/KeilerHirsch/WOLPERTINGER/branches/main":
            return make_branch_payload(head)
        if "WOLPERTINGER/actions/workflows/ci.yml/runs" in path:
            self.assertIn(f"head_sha={head}", path)
            return {"workflow_runs": [make_run(head, "success", 11)]}
        if path.endswith("WOLPERTINGER/releases?per_page=10"):
            return []
        # Return equivalent valid data for PLLDN so the whole snapshot is valid.
        if path == "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator":
            return make_repo_payload("main")
        if path == "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/branches/main":
            return make_branch_payload("b" * 40)
        if "PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/workflows/verify.yml/runs" in path:
            return {"workflow_runs": [make_run("b" * 40, "success", 12)]}
        if path.endswith("PLLDN-Programming-Language-Licensing-Decision-Navigator/releases?per_page=10"):
            return []
        raise AssertionError(path)

    snapshot = self.renderer.collect_snapshot(self.config, get_json)
    project = snapshot["projects"]["WOLPERTINGER"]
    self.assertEqual(project["head"], {"branch": "main", "sha": head})
    self.assertEqual(project["verification"]["state"], "VERIFIED")
```

Add separate tests for stale, failed, missing and malformed evidence:

```python
def test_stale_success_never_verifies_current_head(self):
    # API query is for current head, but a malformed/stale response returns another SHA.
    # Expected: UNKNOWN, never VERIFIED.


def test_current_head_failure_maps_to_fail(self):
    # Matching head_sha + conclusion=failure -> FAIL.


def test_missing_current_head_run_maps_to_unknown(self):
    # Empty workflow_runs -> UNKNOWN.


def test_malformed_repo_or_branch_payload_fails_closed(self):
    # Missing default_branch or commit.sha -> head fields None and verification UNKNOWN.
```

For each test, assert the exact state string.

- [ ] **Step 3: Add failing default-branch and release-binding tests**

Add:

```python
def test_default_branch_is_not_hardcoded_to_main(self):
    # Return default_branch="develop" and assert the collector requests /branches/develop.


def test_public_release_is_shipped_and_resolves_tag_to_commit(self):
    # releases endpoint returns one published non-draft release.
    # /commits/v0.0.1-beta.1 returns {"sha": release_sha}.
    # matching workflow run for release_sha -> release_state SHIPPED and release.verification VERIFIED.


def test_release_does_not_inherit_head_verification_for_different_sha(self):
    # Head SHA is VERIFIED, release SHA differs, release workflow lookup has no run.
    # Expected: project.verification VERIFIED, release.verification UNKNOWN.


def test_release_api_failure_is_unknown_not_shipped(self):
    # get_json raises for releases endpoint.
    # Expected: release_state UNKNOWN and release None.
```

- [ ] **Step 4: Run the focused tests and confirm RED**

Run:

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSignalCollectionTests -v
```

Expected: failures because the current collector still returns `ci` and does not fetch repository/default-branch HEAD evidence.

- [ ] **Step 5: Commit the test contract**

```bash
git add tests/test_profile_signal.py tests/fixtures/signal-snapshot.json
git commit -m "test: define profile evidence v2 contract"
```

---

### Task 2: Implement exact-HEAD and release evidence collection

**Files:**
- Modify: `tools/render_profile_signal.py`
- Test: `tests/test_profile_signal.py`

**Interfaces:**
- Consumes: `profile.json` records and a `get_json(path: str) -> Any` callable.
- Produces:
  - `normalize_verification(conclusion: str | None) -> str`
  - `_workflow_evidence(repo: str, workflow: str, sha: str, get_json: Callable[[str], Any]) -> dict[str, Any]`
  - `_collect_project_snapshot(project: dict[str, Any], get_json: Callable[[str], Any]) -> dict[str, Any]`
  - `collect_snapshot(config: dict[str, Any], get_json: Callable[[str], Any]) -> dict[str, Any]`

- [ ] **Step 1: Replace CI naming with explicit verification naming**

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

Update tests that currently call `normalize_ci` to assert the new vocabulary.

- [ ] **Step 2: Add safe GitHub API helpers**

Import URL helpers:

```python
from urllib.parse import quote, urlencode
```

Add:

```python
def _safe_get_json(get_json: Callable[[str], Any], path: str) -> Any | None:
    try:
        return get_json(path)
    except Exception:
        return None


def _workflow_evidence(
    repo: str,
    workflow: str,
    sha: str,
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    query = urlencode({"head_sha": sha, "status": "completed", "per_page": 1})
    path = (
        f"/repos/{repo}/actions/workflows/{quote(workflow, safe='')}/runs?{query}"
    )
    payload = _safe_get_json(get_json, path)
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list) or not runs or not isinstance(runs[0], dict):
        return {
            "state": UNKNOWN,
            "workflow": workflow,
            "run_id": None,
            "url": "",
            "completed_at": None,
        }

    run = runs[0]
    if run.get("head_sha") != sha:
        return {
            "state": UNKNOWN,
            "workflow": workflow,
            "run_id": run.get("id"),
            "url": run.get("html_url") or "",
            "completed_at": run.get("updated_at"),
        }

    return {
        "state": normalize_verification(run.get("conclusion")),
        "workflow": workflow,
        "run_id": run.get("id"),
        "url": run.get("html_url") or "",
        "completed_at": run.get("updated_at"),
    }
```

The `head_sha` equality check is mandatory even though the request is filtered by SHA; it protects against malformed fixtures/API responses and keeps the rule explicit.

- [ ] **Step 3: Add default-branch HEAD collection**

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

- [ ] **Step 4: Add public release collection and independent release verification**

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
        release_verification = _workflow_evidence(
            repo, workflow, release_sha, get_json
        )
    else:
        release_verification = {
            "state": UNKNOWN,
            "workflow": workflow,
            "run_id": None,
            "url": "",
            "completed_at": None,
        }

    return "SHIPPED", {
        "name": newest.get("name") or tag or "Unnamed release",
        "tag": tag or "",
        "published_at": newest["published_at"],
        "url": newest.get("html_url") or "",
        "sha": release_sha,
        "verification": release_verification,
    }
```

- [ ] **Step 5: Replace `collect_snapshot` with per-project v2 collection**

Add:

```python
def _collect_project_snapshot(
    project: dict[str, Any],
    get_json: Callable[[str], Any],
) -> dict[str, Any]:
    repo = project["repo"]
    workflow = project["workflow"]
    head = _collect_head(repo, get_json)

    if head.get("sha"):
        verification = _workflow_evidence(repo, workflow, head["sha"], get_json)
    else:
        verification = {
            "state": UNKNOWN,
            "workflow": workflow,
            "run_id": None,
            "url": "",
            "completed_at": None,
        }

    release_state, release = _collect_release(
        repo, workflow, head, verification, get_json
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

Delete the old latest-completed-`main` workflow lookup.

- [ ] **Step 6: Update the live-mode test fake API**

The fake must now handle repository metadata, branch HEAD, workflow, releases and optional tag-to-commit lookups. Verify `Authorization: Bearer test-token` is still sent whenever a token exists.

Use assertions that the generated SVG ultimately contains `VERIFIED`, not the old `CI PASS` wording.

- [ ] **Step 7: Run the collection suite and confirm GREEN**

Run:

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSignalCollectionTests \
  tests.test_profile_signal.PublicApiFallbackTests -v
```

Expected: all collection/fallback tests pass.

- [ ] **Step 8: Commit the collector**

```bash
git add tools/render_profile_signal.py tests/test_profile_signal.py
git commit -m "feat: bind profile verification to exact head"
```

---

### Task 3: Render Current Signal v2 with provenance without visual noise

**Files:**
- Modify: `tools/render_profile_signal.py`
- Modify: `tests/test_profile_signal.py`
- Modify: `tests/fixtures/signal-snapshot.json` only if a test-value correction is needed

**Interfaces:**
- Consumes: normalized v2 snapshot from Task 2.
- Produces: deterministic `render_svg(config, snapshot) -> str` showing product phase, exact-HEAD verification state, SHIPPED marker, short head SHA and latest-release verification.

- [ ] **Step 1: Add failing renderer assertions for the v2 vocabulary**

Update `test_render_is_deterministic_and_valid_svg` to assert:

```python
self.assertIn("CURRENT SIGNAL", first)
self.assertIn("WOLPERTINGER", first)
self.assertIn("BUILDING", first)
self.assertIn("VERIFIED", first)
self.assertIn("SHIPPED", first)
self.assertIn("main@1111111", first)
self.assertIn("PLLDN v0.0.1 Beta 1", first)
self.assertNotIn("CI PASS", first)
```

Add a test with a project state of `FAIL` and another with `UNKNOWN`; assert both strings are rendered exactly and the SVG remains valid XML.

- [ ] **Step 2: Add small rendering helpers**

Replace `_status_color` with explicit evidence-state naming:

```python
def _verification_color(state: str) -> str:
    return {
        VERIFIED: "#67e480",
        FAIL: "#ff5f56",
        UNKNOWN: "#9aa4b2",
    }.get(state, "#9aa4b2")


def _short_sha(value: Any) -> str:
    return str(value)[:7] if isinstance(value, str) and value else "unknown"


def _project_state_label(project_snapshot: dict[str, Any]) -> str:
    verification = project_snapshot.get("verification")
    state = verification.get("state") if isinstance(verification, dict) else UNKNOWN
    if state not in {VERIFIED, FAIL, UNKNOWN}:
        state = UNKNOWN
    if project_snapshot.get("release_state") == "SHIPPED":
        return f"{state} · SHIPPED"
    return state
```

- [ ] **Step 3: Update `latest_release` for the v2 schema**

Only `release_state == "SHIPPED"` with a dictionary release may participate:

```python
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

- [ ] **Step 4: Redesign the SVG into a compact command-center panel**

Keep one SVG, monospace typography and the existing dark visual language. Increase the canvas only enough for provenance detail; target `1200x390`.

Each selected project row must contain:

```text
KEY                 PRODUCT PHASE                    VERIFIED · SHIPPED
                    main@abcdef1 · workflow.yml
```

Derive the detail string with:

```python
head = project_snapshot.get("head", {})
verification = project_snapshot.get("verification", {})
branch = head.get("branch") if isinstance(head, dict) else None
sha = head.get("sha") if isinstance(head, dict) else None
workflow = verification.get("workflow") if isinstance(verification, dict) else None
provenance = f"{branch or 'unknown'}@{_short_sha(sha)} · {workflow or 'workflow unknown'}"
```

For the bottom release block, render:

```text
LATEST SHIP         PLLDN v0.0.1 Beta 1 · VERIFIED
EVIDENCE            exact-HEAD · GitHub Actions
```

The release suffix comes from `release["verification"]["state"]`; if absent/malformed, render `UNKNOWN`.

Update SVG accessibility text to:

```xml
<title id="title">Current Signal</title>
<desc id="desc">Current focus, product phase, exact-HEAD verification state, public release state, and GitHub Actions provenance.</desc>
```

Keep every user/API-derived text value passed through `_safe()`.

- [ ] **Step 5: Run renderer tests and inspect a fixture render**

Run:

```bash
python -m unittest tests.test_profile_signal.ProfileSignalTests -v
python tools/render_profile_signal.py \
  --config profile.json \
  --snapshot tests/fixtures/signal-snapshot.json \
  --output /tmp/profile-signal-v2.svg
```

Expected: unit tests pass; `/tmp/profile-signal-v2.svg` parses as XML and contains `VERIFIED`, `SHIPPED`, `main@1111111`, and no `CI PASS`.

- [ ] **Step 6: Commit the v2 renderer**

```bash
git add tools/render_profile_signal.py tests/test_profile_signal.py tests/fixtures/signal-snapshot.json
git commit -m "feat: render provenance-aware profile signal"
```

---

### Task 4: Rebuild the README as the 40%-nerd professional landing page

**Files:**
- Modify: `README.md`
- Modify: `tests/test_profile_signal.py`
- Keep: `assets/profile-hero.webp`

**Interfaces:**
- Consumes: existing hero and `assets/current-signal.svg`.
- Produces: final section order `Hero -> Current Signal -> Selected Work -> How I Build -> Engineering DNA -> Security & Forensics -> MAYHEM Club -> Footer -> hidden source Easter egg`.

- [ ] **Step 1: Rewrite the README surface-contract test first**

Replace the old 250–350-word/three-principle assumptions with these checks:

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
```

Keep the hero-before-signal-before-selected-work assertions and canonical-link assertions.

Assert exactly four principle bullets in `How I build`.

- [ ] **Step 2: Run the README contract and confirm RED**

Run:

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSurfaceContractTests.test_readme_contract -v
```

Expected: fail because the current README does not yet contain Engineering DNA, exact qualification wording or the new hero copy.

- [ ] **Step 3: Replace `README.md` with the approved concise narrative**

Use this copy as the implementation target; wording may only be adjusted for grammar/line wrapping without changing factual claims:

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

- [ ] **Step 4: Run the README contract and full surface tests**

Run:

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSurfaceContractTests -v
```

Expected: all surface-contract tests pass.

- [ ] **Step 5: Commit the landing page**

```bash
git add README.md tests/test_profile_signal.py
git commit -m "docs: rebuild profile command center"
```

---

### Task 5: Authenticate the scheduled renderer and regenerate the public signal asset

**Files:**
- Modify: `.github/workflows/profile-signal.yml`
- Modify: `tests/test_profile_signal.py`
- Regenerate: `assets/current-signal.svg`

**Interfaces:**
- Consumes: the renderer CLI already used by the workflow.
- Produces: an authenticated scheduled/manual GitHub API refresh while retaining the conditional commit behavior.

- [ ] **Step 1: Add a failing workflow-contract assertion for explicit token wiring**

In `test_workflow_contract`, add:

```python
self.assertIn("GITHUB_TOKEN: ${{ github.token }}", text)
```

Retain existing assertions for:

```python
self.assertIn("workflow_dispatch:", text)
self.assertIn("cron: '17 */6 * * *'", text)
self.assertIn("contents: write", text)
self.assertIn("python -m unittest discover -s tests -v", text)
self.assertIn("git diff --quiet -- assets/current-signal.svg", text)
self.assertIn("git commit -m \"chore: refresh profile signal\"", text)
```

- [ ] **Step 2: Run the workflow contract and confirm RED**

Run:

```bash
python -m unittest \
  tests.test_profile_signal.ProfileSurfaceContractTests.test_workflow_contract -v
```

Expected: fail because the current render step does not explicitly export `github.token` as `GITHUB_TOKEN`.

- [ ] **Step 3: Wire the token only into the render step**

Change the render step to:

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

Do not widen repository permissions or add new secrets.

- [ ] **Step 4: Run the complete test suite**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Generate the public SVG from live public evidence**

Run:

```bash
python tools/render_profile_signal.py \
  --config profile.json \
  --output assets/current-signal.svg
```

Expected: exit code `0`; the file contains one of `VERIFIED`, `FAIL`, or `UNKNOWN` for each configured project, and contains exact-head provenance text rather than `CI PASS`.

If the local environment has `GITHUB_TOKEN`, it will be used. If not, the public-repo fallback must still work; do not substitute hand-edited status values.

- [ ] **Step 6: Validate the generated SVG and test suite again**

Run:

```bash
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
text = Path("assets/current-signal.svg").read_text(encoding="utf-8")
ET.fromstring(text)
assert "CURRENT SIGNAL" in text
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

### Task 6: Final audit, public-safety review and PR handoff

**Files:**
- Read/review: all files changed in Tasks 1–5
- No new production files expected

**Interfaces:**
- Consumes: complete branch.
- Produces: one reviewable PR with evidence that copy, tests and exact-HEAD semantics match the frozen spec.

- [ ] **Step 1: Run all deterministic verification commands**

```bash
python -m unittest discover -s tests -v
git diff --check
git status --short
```

Expected: tests pass; `git diff --check` produces no output; working tree contains no unexpected edits.

- [ ] **Step 2: Run a public-copy safety audit**

Run:

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

- [ ] **Step 3: Inspect the commit range**

```bash
git log --oneline --decorate --max-count=12
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- README.md profile.json tools/render_profile_signal.py tests/test_profile_signal.py tests/fixtures/signal-snapshot.json .github/workflows/profile-signal.yml
```

Check specifically that:

- no evidence state was hard-coded into `profile.json`,
- no stale-run path remains in the collector,
- no private-context material leaked into public files,
- no Airbus course-level claim appears,
- no external vanity service was added,
- the README source Easter egg is invisible in rendered Markdown,
- generated SVG is the only generated file changed.

- [ ] **Step 4: Confirm the branch is based on the intended current `main`**

```bash
git fetch origin
git rev-parse origin/main
git merge-base --is-ancestor origin/main HEAD
```

Expected: the ancestry check exits `0`. If `origin/main` advanced during implementation, stop and rebase/merge only through the normal non-destructive workflow approved for the execution session; never force-update history.

- [ ] **Step 5: Open the PR with a concise factual description**

Suggested title:

```text
docs: rebuild profile command center with exact-head evidence
```

Suggested body:

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

- [ ] **Step 6: Review the PR diff before merge**

Use the repository's normal review/outward gate. The final acceptance question is not “does it look cool?” but:

```text
Can a visitor understand within ~20–30 seconds what KeilerHirsch builds,
why the engineering is assurance-heavy, and which visible evidence supports it?
```

Do not merge if exact-HEAD evidence semantics, qualification wording or public-safety constraints are ambiguous.

---

## Self-review record

### Spec coverage

- Hero / builder-first identity: Task 4.
- Current Signal exact-HEAD semantics: Tasks 1–3.
- Fail-closed stale/malformed evidence: Tasks 1–2.
- Public releases and separate release verification: Tasks 1–3.
- Future ATTESTED intentionally excluded: Global Constraints.
- Selected Work WOLPERTINGER + PLLDN: Task 4.
- Four engineering principles + dry humor: Task 4.
- Ada/SPARK primary language and invariant line: Task 4.
- Precision Mechanic / Heinze 13/24 / Electronics Technician / Bundeswehr / autodidact: Task 4.
- Languages: Task 4.
- Security & Forensics remains secondary: Task 4.
- MAYHEM compact: Task 4.
- Stealth canonical Easter egg: Task 4.
- Mobile-oriented compactness: Tasks 3–4.
- Workflow authentication and test-before-render behavior: Task 5.
- Public truthfulness and Airbus boundary: Tasks 4 and 6.

### Placeholder scan

No `TBD`, `TODO`, “implement later”, unspecified error handling, or “similar to” instructions are permitted in this plan. Every behavioral task contains concrete interfaces, assertions, commands and expected outcomes.

### Type / vocabulary consistency

- Verification states: `VERIFIED | FAIL | UNKNOWN` everywhere.
- Release state: `SHIPPED | NONE | UNKNOWN` everywhere.
- Product phase remains `project["status"]` from `profile.json` and is never used as evidence.
- Workflow filename remains `project["workflow"]`.
- Exact HEAD is represented by `head.branch` + `head.sha`.
- Release verification is nested under `release.verification` and never inherited from current HEAD unless the release SHA is exactly the current HEAD SHA.
