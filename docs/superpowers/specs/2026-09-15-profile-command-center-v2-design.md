# KeilerHirsch Profile Command Center v2 — Design

**Status:** Frozen design, implementation not started  
**Date:** 2026-09-15  
**Repository:** `KeilerHirsch/KeilerHirsch`

## 1. Purpose

The GitHub profile is the public technical calling card for KeilerHirsch.

It must explain, within roughly 20–30 seconds:

1. what is being built,
2. why the engineering style is unusually assurance-heavy,
3. what public work proves that claim,
4. where the security / forensic mindset comes from,
5. enough personal engineering background to make the profile human and credible without becoming a résumé wall.

The profile is **builder-first**. Security research, digital forensics and OSINT explain why the engineering differs; they are not a competing public identity.

## 2. Public identity

Primary positioning:

> **Simple products. Uncomfortably serious engineering underneath.**

Supporting line:

> High-assurance software · security research · deterministic systems · reproducible evidence

The profile should read as a coherent story:

`physical engineering → aircraft technology → military service → industrial electrical engineering → self-taught software/security → high-assurance systems → public GitHub work`

Target information density: **40% nerd / 60% professional landing page**.

Avoid:

- badge soup,
- GitHub-stat slot machines,
- generic skill walls,
- inflated claims,
- consultant buzzwords,
- terminal cosplay,
- long résumé prose.

## 3. Page structure

The README should use this order:

1. Hero
2. Current Signal v2
3. Selected Work
4. How I Build
5. Engineering DNA
6. Security & Forensics
7. MAYHEM Club
8. Footer
9. Hidden README-source Easter egg

Mobile rule: within about two screen heights, a visitor should understand what KeilerHirsch builds, what is active now, whether the selected work is verified, and where to click.

## 4. Hero

Keep the existing hero asset unless a later explicit redesign is approved.

Visible copy should stay compact:

> **Simple products. Uncomfortably serious engineering underneath.**
>
> High-assurance software · security research · deterministic systems · reproducible evidence

Primary links remain compact and secondary to the identity message.

No technology badge row.

## 5. Current Signal v2

The existing `Current Signal` concept stays and becomes a provenance-aware public proof panel.

### 5.1 Separation of concerns

Product phase and evidence state are separate.

Examples of product phase:

- BUILDING
- BETA 1
- STABLE

Examples of evidence state:

- VERIFIED
- FAIL
- UNKNOWN
- SHIPPED
- future: ATTESTED

A manually configured product phase must never imply technical verification.

### 5.2 VERIFIED semantics

`VERIFIED` may be shown only when the configured verification workflow has completed successfully for the **exact current default-branch HEAD SHA**.

The old behavior — taking the latest completed workflow run on `main` regardless of whether it belongs to the current HEAD — is insufficient and must be replaced.

Fail closed:

- successful run for an older SHA → not VERIFIED,
- no run for current SHA → UNKNOWN,
- failed current-SHA run → FAIL,
- ambiguous or malformed API data → UNKNOWN.

Do not infer green status from stale evidence.

### 5.3 SHIPPED semantics

`SHIPPED` requires a real public GitHub release.

Release state and verification state remain distinct. A release existing does not automatically mean the released commit is verified.

Where practical, the renderer should resolve the release tag / target to a concrete commit and expose enough provenance to distinguish:

- current HEAD verification,
- release existence,
- release-commit verification.

### 5.4 Future ATTESTED state

`ATTESTED` is reserved for actual verifiable build / artifact provenance such as GitHub Artifact Attestations.

Do not display it until the underlying evidence exists and is checked.

### 5.5 Visual density

Normal rendering should remain readable to non-specialists.

Preferred shape:

```text
CURRENT SIGNAL

FOCUS
WOLPERTINGER — Presentation subsystem

WOLPERTINGER     BUILDING      VERIFIED
PLLDN            BETA 1        VERIFIED · SHIPPED

LATEST SHIP
PLLDN v...

EVIDENCE
exact-HEAD · GitHub Actions · refreshed ... UTC
```

A short SHA may be included where useful. Full SHA / deeper provenance belongs in source data or optional detail, not as visual noise.

A red FAIL is allowed and should not be cosmetically hidden.

## 6. Selected Work

Show a small curated set, not a repository catalog.

### 6.1 WOLPERTINGER

Role: flagship systems / product engineering proof.

Suggested positioning:

> **One core. Multiple presentation surfaces.**
>
> An Elite Dangerous companion platform built around deterministic replay, provenance, explicit trust boundaries and a narrow high-assurance core.

### 6.2 PLLDN

Role: deterministic decision-engineering / product UX proof.

Suggested positioning:

> **Decisions you can defend.**
>
> A deterministic language and licensing navigator where explicit project facts stay authoritative and free text never becomes an oracle.

Links may include live app, repository and latest release.

### 6.3 Critical FAR Disclosure

Do not elevate it to equal prominence until the public repository contains enough substance to function as evidence rather than a placeholder.

Once ready, it can become the third major proof point for security / forensic evidence engineering.

## 7. How I Build

Keep this concise and principle-driven.

Preferred principles:

### Evidence before claims

Tests, provenance and reproducible artifacts should support what a README says.

### Over State of the Art by default

“Good enough” is a release decision, not an engineering philosophy.

### Deterministic where it matters

Core decisions should come from explicit rules and traceable facts whenever possible.

### KISS outside. Assurance inside.

Complexity belongs behind the user-facing surface. Critical boundaries get stronger assurance when the architecture benefits from it.

Dry-humor line:

> *If the UI looks simple, someone probably suffered in the architecture first.*

## 8. Engineering DNA

This section explains the origin of the engineering mindset without becoming a conventional CV.

### 8.1 Ada/SPARK

Ada/SPARK should be visible as the primary high-assurance engineering language, but never framed as exoticism or status signaling.

Preferred wording:

> **Ada/SPARK is my primary engineering language.** Not because obscurity is a personality trait, but because I do not like compromising at critical boundaries.
>
> **I would rather prove an invariant than explain later why “that should never happen” happened.**

Also make the pragmatic boundary explicit:

> I still use C#, Python, JavaScript and whatever else fits the job. Not every component needs SPARK — but critical correctness is not where I like to negotiate.

### 8.2 Physical-engineering background

Public-safe, factual chain:

- **Precision Mechanic** (`Feinwerkmechaniker`) — completed German vocational qualification / journeyman qualification.
- **State-Certified Technician program in Mechanical Engineering — Aircraft Technology specialization** at Technische Fachschule Heinze, Hamburg — **13 of 24 full-time months completed; no qualification awarded**.
- **Electronics Technician for Industrial Engineering** (`Elektroniker für Betriebstechnik`) — completed German IHK vocational qualification. This English occupation label follows the BIBB translation; do not reduce the German occupation to “electrician”.
- **23 months of voluntary military service in the German Armed Forces (Bundeswehr)**.
- extensive **self-taught / autodidactic** work in software engineering, security research, digital forensics, OSINT and systems engineering.

Important accuracy constraint:

Do **not** call the Heinze program a university degree or imply an Aerospace Engineer / state-certified technician title was earned.

Do **not** claim that the user’s specific 2004 cohort was formally an Airbus cooperation program unless direct course-level evidence is later found. It is acceptable to state the school / program’s aircraft-technology context; Airbus may only be mentioned in personal-course context if specifically evidenced.

### 8.3 Mindset bridge

Preferred narrative:

> That background shaped how I approach software: tolerances, measurements, failure modes, maintainability and systems first — syntax second.

Optional bridge sentence:

> **GitHub is where the workshop became software — and the measurements stayed.**

This should explain why the profile owner tends to escalate “small tools” into more defensible systems: the default is to measure, verify and make failure explicit rather than assume.

### 8.4 Spoken languages

Keep compact:

> **Languages:** Polish (native) · German (fluent / native-level) · English (very good)

### 8.5 Humor

One light line may acknowledge the early technical hobby background:

> *Formal education helped. So did a suspicious amount of self-teaching — and, apparently, 9th-grade Realschule Technik-AG.*

Do not turn this section into a joke block.

## 9. Security & Forensics

Keep intentionally small so the public identity stays builder-first.

Suggested copy:

> I approach systems with the same mindset I use to build them: preserve evidence, bind claims to sources, separate observation from inference, and make important state reproducible.
>
> Focus: AI systems · agent tooling · digital forensics · OSINT · provenance

Future FAR work can become the concrete proof artifact for this section.

## 10. MAYHEM Club

Reduce the current long community explanation to a compact human / community signal.

Suggested copy:

> Founder & Mod of `r/MAYHEMClub` — a creator-first workshop for indie devs, modders, open-source builders and people shipping wonderfully weird things.
>
> **Build cool shit. Share it. Get real feedback.**

Do not reproduce community rules on the personal profile.

## 11. Humor policy

Humor should be dry, sparse and placed after credibility has already been established.

Approved tone examples:

- `Simple products. Uncomfortably serious engineering underneath.`
- `If the UI looks simple, someone probably suffered in the architecture first.`
- `Simple outside. Technically unpleasant to copy inside.`

Avoid turning project descriptions, assurance claims or education details into jokes.

## 12. Easter egg

The personal canonical Easter egg is:

> **The Man, The Myth, The Legend — KeilerHirsch**

For this profile, implement it as a **stealth README HTML comment** visible only to someone reading the Markdown source.

Suggested form:

```html
<!--
🥚 You looked behind the curtain.

The Man, The Myth, The Legend.
— KeilerHirsch

The UI was the easy part.
-->
```

Do not advertise the existence of the Easter egg in the rendered README.

It must remain harmless, dependency-free, tracking-free and accessibility-neutral.

## 13. Technical implementation scope

Expected implementation files:

- `README.md`
- `profile.json`
- `tools/render_profile_signal.py`
- `tests/test_profile_signal.py`
- `tests/fixtures/*` as needed
- `.github/workflows/profile-signal.yml` only where required by the revised evidence flow
- generated `assets/current-signal.svg`

No external stats service or tracking dependency is required.

## 14. Testing requirements

At minimum, tests must cover:

1. exact current HEAD with successful configured workflow → VERIFIED,
2. successful workflow only for older SHA → UNKNOWN, never VERIFIED,
3. failed workflow for current SHA → FAIL,
4. no workflow result → UNKNOWN,
5. malformed / incomplete API response → fail closed,
6. public release detection,
7. release target / commit resolution where supported,
8. release existence does not imply release verification,
9. HTML escaping in SVG text,
10. deterministic rendering from a fixed snapshot,
11. atomic output behavior remains intact,
12. generated SVG remains readable with the expected small project set.

The existing test-first renderer workflow should be preserved.

## 15. Public-safety / truthfulness rules

This is a public repository.

- No private conversation details.
- No family / health / financial context.
- No invented affiliations.
- No unearned academic or professional title.
- No Airbus-course claim without course-specific evidence.
- German regulated / formal qualification names should remain available alongside working English translations where translation could blur meaning.
- Claims about CI, releases, verification or provenance must be derived from evidence, not manually decorated.

## 16. Definition of done

The redesign is complete when:

- the first screen establishes the builder-first high-assurance identity,
- Current Signal uses exact-HEAD evidence semantics and fails closed,
- WOLPERTINGER and PLLDN are the primary visible proof projects,
- Ada/SPARK is clearly but non-dogmatically positioned as the primary high-assurance language,
- the physical-engineering / Bundeswehr / autodidactic background is visible without becoming a CV wall,
- education wording is factually bounded,
- security / forensic work supports rather than competes with the builder identity,
- MAYHEM remains visible but compact,
- the source Easter egg exists and is not advertised,
- mobile readability remains strong,
- tests cover the new evidence semantics,
- no external vanity-stat dependency has been introduced.
