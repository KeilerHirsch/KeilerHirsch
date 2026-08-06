<div align="center">

# KeilerHirsch

[![myrank.dev](https://myrank.dev/api/badge/KeilerHirsch?style=profile)](https://myrank.dev/u/KeilerHirsch)

**Bughunter.** OSINT & digital forensics meets AI agent engineering.

I break the tools I run — then harden them. Measure, don't guess.

🔬 [KeilerHirsch-Labs](https://github.com/KeilerHirsch-Labs) — the org for tools meant to stand on their
own, separate from the experiments below.

</div>

---

I build and harden the tools I actually run: AI agent workflows in Go and Python, game mods in Lua.
Self-taught from electrical and trades work into security research and systems tooling. When a tool I
depend on breaks, I root-cause it and send a tested fix upstream instead of working around it forever.

## 🛠️ AI tooling & agent workflows

- **[ai-trinity](https://github.com/KeilerHirsch/ai-trinity)** — *core project.* The three things that
  make an AI coding setup actually reliable: a model that isn't dumb, a real harness, persistent memory.
  Problem → thesis → buildable solution, EN/DE, from months of hands-on iteration rather than theory.
- **[schroedinger-sync](https://github.com/KeilerHirsch-Labs/schroedinger-sync)** — single Go binary that
  exports your claude.ai conversations, project docs and memory to local Markdown. Windows, DPAPI + CDP,
  no telemetry, no cloud. Now under [KeilerHirsch-Labs](https://github.com/KeilerHirsch-Labs).
- **[claude-bordcomputer-sounds](https://github.com/KeilerHirsch/claude-bordcomputer-sounds)** —
  Star-Trek ship's-computer acoustic hooks for Claude Code auto-mode workflows.

## 🤝 Upstream contributions

Tested patches and root-caused reports against code I run — no drive-by issues.

- **[MemPalace/mempalace](https://github.com/MemPalace/mempalace)** — my daily long-term memory store.
  Three merged fixes, all found by running it under real load: MCP startup deadlock
  ([#1987](https://github.com/MemPalace/mempalace/pull/1987)), cross-device rename breaking in-place
  archive repair ([#1945](https://github.com/MemPalace/mempalace/pull/1945)), and a miner flooding the
  store with raw tool dumps ([#2010](https://github.com/MemPalace/mempalace/pull/2010)).
- **Farming Simulator 25 mods** — dedicated-server bugs from a live multiplayer server, submitted as
  patches with reproduction and log evidence attached:
  [Courseplay](https://github.com/Courseplay/Courseplay_FS25/pull/1298) ·
  [AutoDrive](https://github.com/Stephan-S/FS25_AutoDrive/pull/553) ·
  [EnhancedVehicle](https://github.com/ZhooL/FS25_EnhancedVehicle/pull/84) ·
  [BetterContracts](https://github.com/Mmtrx/FS25_BetterContracts/pull/205) ·
  [RedTape](https://github.com/Ozz-Modding/FS25_RedTape/pull/122) ·
  [ToolInclinationHelper](https://github.com/Timmeey86/FS25_ToolInclinationHelper/pull/13) ·
  [UnloadBalesEarly](https://github.com/Timmeey86/FS25_UnloadBalesEarly/pull/33)
- **[Dude23-mods/FS25_Personnel_Management](https://github.com/Dude23-mods/FS25_Personnel_Management)** —
  server-freeze (unbounded network array reads) and fail-open farm-authorization bugs. No license on the
  repo, so reported via Issue — fixed and credited by name twice in the maintainer's v1.1.0.0 notes.

## 👀 Code review

I review PRs the way I ship code: trace the fix to where it's consumed, don't just read the diff, check
the discussion thread before adding to it. 12 PRs reviewed across 10 FS25 modding repos: 8 approved,
3 flagged with concrete findings, 1 changes-requested.

- **[RealisticWeather#170](https://github.com/Arrow-kb/FS25_RealisticWeather/pull/170)** — swapped
  `self`/`superFunc` parameters that would have crashed on every savegame load, proven against the
  codebase's own calling convention.
- **[AutoDrive#544](https://github.com/Stephan-S/FS25_AutoDrive/pull/544)** — read the thread first: the
  change reintroduced a deliberately-fixed regression; backed the maintainers' call with a concrete
  alternative.
- **[ContractBoost#122](https://github.com/GMNGjoy/FS25_ContractBoost/pull/122)** — likely nil-crash on
  a disabled game feature's UI menu.
- **[ContractBoost#115](https://github.com/GMNGjoy/FS25_ContractBoost/pull/115)** — hardcoded engine
  constant nobody had verified against the base game.

## 🚜 Farming Simulator 25 — mods & server tooling

My proving ground: a real dedicated server, real multiplayer, real players hitting real bugs.
Multiplayer is where sloppy code actually breaks — honest training for the security work.

- **[FS25_IronHorseRealism](https://github.com/KeilerHirsch/FS25_IronHorseRealism)** — modular
  vehicle-realism framework.
- **[FS25_16xMapFix](https://github.com/KeilerHirsch/FS25_16xMapFix)** — verified fix for the 16x-map
  "freezes at 100% compiling shaders" bug.
- **[FS25_AutoVRAMOptimizer](https://github.com/KeilerHirsch/FS25_AutoVRAMOptimizer)** — auto-raises the
  texture-streaming VRAM budget to match your card.
- **[FS25_NoResetMP](https://github.com/KeilerHirsch/FS25_NoResetMP)** — hardcore multiplayer: no free
  vehicle "reset to shop".
- **[FS25_SoundOverhaulRealism](https://github.com/KeilerHirsch/FS25_SoundOverhaulRealism)** —
  engine-accurate vehicle sounds (I6/V8), strictly CC0 / self-recorded.
- **[fs25-server-watch](https://github.com/KeilerHirsch/fs25-server-watch)** — zero-dependency dedicated
  server monitor: live status, joins, crashes.

## ⚖️ Consumer rights

- **[reach-a-human](https://github.com/KeilerHirsch/reach-a-human)** — bypasses AI customer-service bots
  to reach a real human, and documents GDPR/CCPA rights when companies hide behind automation.

## 🔍 Security research

I hunt bugs in code I actually run — game mods, AI tooling, agent CLIs — and report tested patches,
not drive-by issues.

- **Recurring multiplayer vuln class across 5 independent FS25 mod authors**: server-authoritative
  network events missing the origin check their siblings have, letting a modified client spoof fake
  server messages and overwrite protected state. 7 issues filed — economy exploits (forged invoices,
  unlimited money, forged crop quality in
  [MoistureSystem](https://github.com/Ozz-Modding/FS25_MoistureSystem/issues/63)), a cross-farm exploit
  with crash vector in
  [EnhancedAnimalSystem](https://github.com/Chissel/FS25_EnhancedAnimalSystem/issues/45), and an
  unbounded-read DoS.
- **Server-freeze + fail-open farm-authorization** in a mod — fixed and credited by name twice in the
  maintainer's release notes.
- **Dedicated-server crash and data-loss bug** in two other mods — root-caused by bisecting live server
  and client logs, submitted as PRs.
- **Gen-5 audit + model pinning** — measured, independently fact-checked evidence on Claude generation 5
  (nonsense detection, verbosity, under-disclosed model fallback) and on silent model-pinning bypasses in an
  agent CLI, with reproducible protocols:
  [full write-up](https://gist.github.com/KeilerHirsch/5e212e6f9fb6fd670f191920eea4cb78) ·
  [pinning reproduction protocol v2](https://github.com/KeilerHirsch/ai-trinity/blob/main/docs/audit-claude-gen5/pinning-vektoren-messprotokoll-v2.1.223.md) ·
  [issue #83795](https://github.com/anthropics/claude-code/issues/83795).

Coordinated disclosure only. No public details before a fix ships — and I don't claim other people's CVEs.

## ⚙️ How I work

"Works on my machine" is not a standard. Every repo here clears the same floor:

- **CI on every push** — lint and tests, so green means something
- **Explicit license** — no license means all rights reserved
- **Tests before release**, not after the bug report
- **Adversarial second pass** before shipping — its only job is to find what I missed
- **Root cause over band-aid** — hypothesis → reproduction → evidence → fix
- **Measure, never guess** — a claim without a number is a hunch wearing a lab coat

---

<div align="center">

📫 **Open an issue on any repo above** — that's the reliable way to reach me.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-FF5E5B?style=flat&logo=kofi&logoColor=white)](https://ko-fi.com/keilerhirsch)

</div>
