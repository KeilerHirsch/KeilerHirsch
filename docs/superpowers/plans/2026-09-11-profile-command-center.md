# Profile Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a concise personal GitHub README with an approved hero and one self-hosted dynamic engineering-status panel.

**Architecture:** A tiny checked-in `profile.json` holds manual product state. A Python-standard-library renderer fetches allowlisted GitHub workflow/release metadata and writes one deterministic SVG; a scheduled Action updates only that SVG when bytes change.

**Tech Stack:** Markdown, JSON, Python 3 standard library, SVG, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-11-profile-command-center-design.md`

## Global Constraints

- README stays roughly 250–350 words and contains no badge/statistics wall.
- Public API data comes only from configured repositories.
- Equal config + snapshot must render identical SVG bytes.
- Network/render failure must not replace the last valid SVG.
- No third-party runtime dependency or external badge service.
- Workflow commits only when the generated SVG changes.

---

### Task 1: Deterministic Current Signal renderer

**Files:**
- Create: `profile.json`
- Create: `tools/render_profile_signal.py`
- Create: `tests/test_profile_signal.py`
- Create: `tests/fixtures/signal-snapshot.json`
**Interfaces:**
- Consumes: `profile.json` and optional snapshot JSON for offline verification.
- Produces: deterministic `assets/current-signal.svg`.

- [ ] Write tests for config validation, deterministic rendering, CI normalization, release selection, XML escaping, and fail-before-write behavior.
- [ ] Run `python -m unittest discover -s tests -v` and confirm RED because the renderer does not exist.
- [ ] Implement the minimal renderer and GitHub API collector with `urllib.request`.
- [ ] Run the unit suite and confirm GREEN.
- [ ] Render the checked-in SVG from the deterministic fixture.

### Task 2: GitHub automation

**Files:**
- Create: `.github/workflows/profile-signal.yml`
- Extend: `tests/test_profile_signal.py`

**Interfaces:**
- Consumes: `profile.json`, repository `GITHUB_TOKEN`, renderer CLI.
- Produces: an updated `assets/current-signal.svg` commit only when bytes differ.

- [ ] Add failing static-contract tests for schedule, manual trigger, least permissions, exact renderer invocation, and diff-gated commit.
- [ ] Run tests and confirm RED.
- [ ] Add the workflow with a six-hour cron and `workflow_dispatch`.
- [ ] Run tests and confirm GREEN.

### Task 3: Product-first profile README and hero

**Files:**
- Modify: `README.md`
- Create: `assets/profile-hero.webp`
- Extend: `tests/test_profile_signal.py`

**Interfaces:**
- README embeds the hero and Current Signal SVG and links WOLPERTINGER, PLLDN, MyRank, Ko-fi, and `r/MAYHEMClub`.

- [ ] Add failing README-contract tests: hero first, Current Signal before selected work, only three engineering principles, MAYHEM Founder & Mod copy, required canonical links, and word budget.
- [ ] Run tests and confirm RED.
- [ ] Rewrite README to the frozen compact layout and add the approved hero asset.
- [ ] Run full tests, renderer fixture verification, `git diff --check`, and XML parse verification.
- [ ] Commit, run GRANIT II on the exact committed range, push branch, open PR, wait for checks, merge, and verify remote `main`.
