# KeilerHirsch Profile Command Center Design

## Goal

Turn `KeilerHirsch/KeilerHirsch` into a concise GitHub profile landing page with one live engineering-status surface.

## Product rule

**Say less. Show more. Prove the rest below.**

The profile is not a CV, stats wall, or process manual. It should communicate identity, current work, project health, and MAYHEM Club in a few seconds.

## Surface

Order is frozen:

1. Selected electronics-workbench hero.
2. One-line engineering identity + compact links.
3. `CURRENT SIGNAL` generated SVG.
4. Selected work: WOLPERTINGER and PLLDN.
5. Three engineering principles.
6. MAYHEM Club founder/mod callout.
7. End.
## Current Signal contract

`profile.json` is the only manual status input. It contains the current focus and the small allowlist of visible repositories.

Automation reads only public GitHub metadata for those repositories: the configured CI workflow and published releases. It renders `assets/current-signal.svg` with:

- current focus;
- WOLPERTINGER product status + CI;
- PLLDN product status + CI;
- newest published release across the visible repositories.

No stars, contribution counts, commit counts, language percentages, visitor counters, trophies, or activity feeds.

The render is deterministic for equal inputs and contains no generated timestamp. If GitHub API collection or rendering fails, the workflow fails before replacing the last valid SVG. Missing workflow runs are shown as `UNKNOWN`; absence of releases is valid.

## Automation

Run every six hours and through `workflow_dispatch`. The workflow has read access by default and `contents: write` only because it may commit the generated SVG. It commits only when `assets/current-signal.svg` actually changes.

Implementation uses Python standard library only. No third-party runtime dependency or external badge service.

## Visual rules

The hero keeps the approved dark electronics-workbench image and MAYHEM Club copy. The signal panel is quieter: dark instrument panel, restrained red accent, white/gray monospace text, four information rows, no decorative dashboard clutter.

README target: roughly 250–350 words maximum. Deep project detail stays in project repositories.
