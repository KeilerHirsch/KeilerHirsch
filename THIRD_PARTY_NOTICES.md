# Third-Party Notices and External Boundaries

Audit baseline: 2026-09-03.

## GitHub Actions

`.github/workflows/update-profile.yml` references `actions/checkout@v7`. The upstream `actions/checkout` v7 license was rechecked during this audit and is MIT, Copyright © 2018 GitHub, Inc. and contributors.

The action is referenced as an external workflow dependency; its source is not vendored into this repository. Its upstream license and notices continue to govern that action.

## Public GitHub API data

The updater reads public GitHub event, search, repository, pull-request, and release metadata. Repository names, dates, branch names, release tags, URLs, public facts, and third-party PR titles remain subject to their actual source and applicable rights. Rendering those facts into the profile does not create a project copyright claim over them.

## External services and marks

GitHub, MyRank.dev, Ko-fi, hits.sh, Anthropic, Claude, Farming Simulator, GIANTS Software, and other externally named services/projects retain their respective names, marks, content, and rights. External badges/counters are fetched or linked from their providers rather than claimed as project assets.