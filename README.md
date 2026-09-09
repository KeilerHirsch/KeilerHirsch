<div align="center">

# KeilerHirsch

**Evidence-driven software engineering. High-assurance inside. KISS outside.**

I build software that keeps the complicated parts inside the system instead of handing them to the user.

</div>

---

## Current public work

### [WOLPERTINGER](https://github.com/KeilerHirsch/WOLPERTINGER)

An Elite Dangerous companion platform built around one core and multiple presentation surfaces. The goal is not to become tool number 15; it is to stop the Commander from having to coordinate 14 separate tools.

**Status:** active development. Windows-first, cross-platform-ready architecture; high-assurance internals with a low-friction Commander experience as the product target.

### [PLLDN - Programming Language & Licensing Decision Navigator](https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator)

A constraint-first decision navigator for programming-language and licensing choices. It prefers explainable recommendations, explicit unknowns, and deterministic decision paths over hype or decorative confidence scores.

**Status:** `v0.0.1 Beta 1` is public. The live Beta intentionally exposes a narrow reviewed language surface while the broader product evolves behind explicit release gates.

## How I build

- **Product first, machine room second.** A README should explain the outcome before the architecture.
- **High-assurance inside. KISS outside.** Complexity belongs in the implementation, not in the user's startup ritual.
- **Requirements before code.** Architectural work starts with explicit scope, constraints, and acceptance criteria.
- **Evidence before claims.** Tests, review, provenance, and reproducible artifacts are distinct evidence classes; none substitutes for another.
- **Deterministic where it matters.** Core decisions should not depend on fuzzy inference when explicit rules and traceable facts can do the job.
- **Isolated change flow.** Worktree -> implementation -> verification -> review -> PR -> CI -> merge -> true-main verification.
- **Fail closed, recover clearly.** Unknown state stays unknown; errors should explain what failed, what still works, and what action recovers the system.

The engineering process behind these repositories is intentionally stricter than the user experience they expose. That is the point.

## Clean-slate policy

In September 2026 I deliberately reduced my public GitHub surface. Older experiments and historical repositories are preserved, but they are not presented as current engineering quality.

I would rather maintain a small number of repositories I can defend end-to-end than a large portfolio of stale demos, abandoned automation, and inherited workflow debt.

New public work is rebuilt against the current engineering baseline instead of carrying old repository conventions forward by default.

## Links

- [MyRank.dev](https://myrank.dev/u/KeilerHirsch)
- [Ko-fi](https://ko-fi.com/keilerhirsch)

For project-specific questions or bug reports, open an issue in the relevant repository.
