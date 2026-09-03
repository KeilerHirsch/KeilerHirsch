# Rights and Provenance Record

Audit baseline: `00aa2e9949eeb0cafa9a216f4ff2fa2d8ce00762` on 2026-09-03 before the current rights migration.

## Repository history

The audited pre-migration history contains 50 commits. Human-maintainer identities resolve to `KeilerHirsch` / `GSOC` using the maintainer's GitHub noreply identities; automated refresh commits use `github-actions[bot]`. No external human `Co-authored-by:` trailers were found in the audit.

The current tree contains nine tracked paths. The only historical path removed from the current tree before this migration is the earlier root `LICENSE` file described in `LICENSE-HISTORY.md`.

## Human project control

Generative-AI systems and coding assistants may be used as development tools. Human project control includes requirements, profile/editorial positioning, automation behavior, selection/rejection of changes, integration, review, testing, provenance decisions, and final release approval.

No percentage such as "AI-generated code" is used as an authorship shortcut. Rights claims are based on the concrete human-controlled work and the documented chain of title.
## Automation provenance

`scripts/update_profile.py` was introduced on 2026-08-17 after the historical MIT license had already been removed. It uses Python standard-library modules only. `.github/workflows/update-profile.yml` orchestrates that script and uses GitHub's `actions/checkout` action as an external workflow dependency.

Automated README refresh commits are mechanically produced from maintainer-authored automation. The public GitHub facts and third-party titles rendered by that automation are not recharacterized as project-owned content; see `DYNAMIC-DATA.md`.

## Release and change-control evidence

For material rights-sensitive changes, preserve the reviewed commit SHA, CI/test result, relevant provenance/third-party findings, and final maintainer approval. A reusable record template is stored in `docs/provenance/RELEASE_TEMPLATE.md`.

Substantial future external contributions are accepted only after explicit provenance and rights review so that the repository's public and alternative licensing positions remain supportable.