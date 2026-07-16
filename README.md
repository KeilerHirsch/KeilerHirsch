# KeilerHirsch

[![Go](https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white)](https://github.com/KeilerHirsch/schroedinger-sync)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://github.com/KeilerHirsch?tab=repositories)
[![Lua](https://img.shields.io/badge/Lua-2C2D72?style=flat&logo=lua&logoColor=white)](https://github.com/KeilerHirsch?tab=repositories)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-FF5E5B?style=flat&logo=kofi&logoColor=white)](https://ko-fi.com/keilerhirsch)

I build and harden the tools I actually run — AI agent workflows in Go and Python, game mods in Lua.
Self-taught from electrical/trades work into security research and systems tooling. When something breaks
in a tool I depend on, I'd rather root-cause it and send a tested fix upstream than work around it forever.

---

## AI tooling & agent workflows

| Repo | What it is |
|---|---|
| **[ai-trinity](https://github.com/KeilerHirsch/ai-trinity)** | The three things that make an AI coding setup actually reliable: a model that isn't dumb, a real harness, and persistent memory. Problem → thesis → buildable solution, EN/DE, from months of hands-on iteration rather than theory. |
| **[schroedinger-sync](https://github.com/KeilerHirsch/schroedinger-sync)** | Single Go binary that exports your own claude.ai conversations, project docs and memory to local Markdown. Windows, DPAPI + CDP, no telemetry, no cloud dependency. |
| **[mempalace](https://github.com/KeilerHirsch/mempalace)** *(fork — upstream contributor)* | Open-source AI memory system. I run it as my daily long-term memory store and send fixes upstream when I hit real bugs under load. |
| **[claude-bordcomputer-sounds](https://github.com/KeilerHirsch/claude-bordcomputer-sounds)** | Star-Trek ship's-computer acoustic hooks for Claude Code auto-mode workflows. |

## Farming Simulator 25 — mods & server tooling

My proving ground: a real dedicated server, real multiplayer, real players hitting real bugs.
Multiplayer is where sloppy code actually breaks — which makes it honest training for the security work.

| Repo | What it is |
|---|---|
| **[FS25_IronHorseRealism](https://github.com/KeilerHirsch/FS25_IronHorseRealism)** | Original modular vehicle-realism framework for FS25. |
| **[FS25_16xMapFix](https://github.com/KeilerHirsch/FS25_16xMapFix)** | Diagnosis + verified fix for the 16x-map "freezes at 100% compiling shaders" bug. |
| **[FS25_AutoVRAMOptimizer](https://github.com/KeilerHirsch/FS25_AutoVRAMOptimizer)** | Raises the texture-streaming VRAM budget automatically, matched to your card. |
| **[FS25_NoResetMP](https://github.com/KeilerHirsch/FS25_NoResetMP)** | Hardcore multiplayer: disables the free vehicle "reset to shop". |
| **[FS25_SoundOverhaulRealism](https://github.com/KeilerHirsch/FS25_SoundOverhaulRealism)** | Engine-accurate vehicle sounds (I6/V8), built strictly from CC0 / self-recorded audio. |
| **[fs25-server-watch](https://github.com/KeilerHirsch/fs25-server-watch)** | Zero-dependency dedicated-server monitor: live status, joins, crashes. |

## Consumer rights

**[reach-a-human](https://github.com/KeilerHirsch/reach-a-human)** — bypasses AI customer-service bots to reach a
real human, and documents how to exercise GDPR/CCPA rights when a company hides behind automation.

---

## Security research

I hunt bugs in code I actually run — game mods, AI tooling, agent CLIs — and report them as tested patches,
not drive-by issues. Concrete and recent:

- **Multiplayer DoS + authorization bypass** in a third-party FS25 mod: network readers took a client-supplied
  array length with no upper bound (a ~2-billion count in one small packet freezes the single-threaded
  server), and farm authorization failed *open* instead of closed, letting a client act on a farm they don't
  own. Both confirmed by the maintainer and going into the next release.
- **A dedicated-server crash** and a **data-loss bug** in two other mods — root-caused by bisection against
  live server and client logs, then submitted as PRs.
- **Upstream fixes** to the AI memory system I depend on, found by running it under real load rather than
  reading its source.

Coordinated disclosure only. No public details before a fix ships — and I don't claim other people's CVEs.

## How I work

Every repo here clears the same floor, because "works on my machine" is not a standard:

- **CI on every push** — lint and tests, so the green badge means something
- **An explicit license** — no license means all rights reserved, which helps nobody
- **Tests before the release**, not after the bug report
- **Adversarial review before shipping** — a second pass whose only job is to find what I missed
- **Root cause over band-aid** — hypothesis → reproduction → evidence → fix. No "this should help" commits.

---

📫 Open an issue on any repo above — that's the reliable way to reach me.
