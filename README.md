<div align="center">

# KeilerHirsch

[![myrank.dev](https://myrank.dev/api/badge/KeilerHirsch?style=profile)](https://myrank.dev/u/KeilerHirsch)

**OSINT & digital forensics meets AI agent engineering**

</div>

---

I build and harden the tools I actually run — AI agent workflows in Go and Python, game mods in Lua.
Self-taught from electrical/trades work into security research and systems tooling. When something breaks
in a tool I depend on, I'd rather root-cause it and send a tested fix upstream than work around it forever.

## 🛠️ AI tooling & agent workflows

- **[ai-trinity](https://github.com/KeilerHirsch/ai-trinity)**
  The three things that make an AI coding setup actually reliable: a model that isn't dumb, a real harness,
  and persistent memory. Problem → thesis → buildable solution, EN/DE, from months of hands-on iteration
  rather than theory.
- **[schroedinger-sync](https://github.com/KeilerHirsch/schroedinger-sync)**
  Single Go binary that exports your own claude.ai conversations, project docs and memory to local Markdown.
  Windows, DPAPI + CDP, no telemetry, no cloud dependency.
- **[claude-bordcomputer-sounds](https://github.com/KeilerHirsch/claude-bordcomputer-sounds)**
  Star-Trek ship's-computer acoustic hooks for Claude Code auto-mode workflows.

## 🤝 Upstream contributions

I don't file drive-by issues. Everything below is a tested patch or a root-caused report against code I run.

- **[MemPalace/mempalace](https://github.com/MemPalace/mempalace)** — open-source AI memory system, my daily
  long-term memory store. Three merged fixes, all found by running it under real load rather than reading its
  source: an MCP startup deadlock ([#1987](https://github.com/MemPalace/mempalace/pull/1987) — answer
  `initialize` immediately, move preflight off the handshake thread), a cross-device rename that broke
  in-place archive repair ([#1945](https://github.com/MemPalace/mempalace/pull/1945)), and a miner that
  flooded the store with raw agent tool dumps ([#2010](https://github.com/MemPalace/mempalace/pull/2010)).
- **Farming Simulator 25 mods** — dedicated-server bugs found on a live multiplayer server, submitted as
  patches with the reproduction and the log evidence attached:
  [Courseplay](https://github.com/Courseplay/Courseplay_FS25/pull/1298) ·
  [AutoDrive](https://github.com/Stephan-S/FS25_AutoDrive/pull/553) ·
  [EnhancedVehicle](https://github.com/ZhooL/FS25_EnhancedVehicle/pull/84) ·
  [BetterContracts](https://github.com/Mmtrx/FS25_BetterContracts/pull/205) ·
  [RedTape](https://github.com/Ozz-Modding/FS25_RedTape/pull/122) ·
  [ToolInclinationHelper](https://github.com/Timmeey86/FS25_ToolInclinationHelper/pull/13) ·
  [UnloadBalesEarly](https://github.com/Timmeey86/FS25_UnloadBalesEarly/pull/33)
- **[Dude23-mods/FS25_Personnel_Management](https://github.com/Dude23-mods/FS25_Personnel_Management)** —
  server-freeze (unbounded network array reads) and fail-open farm-authorization bugs. No license on the
  repo, so reported via Issue rather than a PR — both fixed and credited by name, twice, in the maintainer's
  own v1.1.0.0 release notes.

## 👀 Code review

I review other people's pull requests the same way I ship my own — trace a fix to where it's actually
consumed, don't just read the diff, and check the discussion thread before adding to it.
12 PRs reviewed across 10 repos in the FS25 modding ecosystem: 8 approved, 3 flagged with concrete findings,
1 changes-requested.

- **[RealisticWeather#170](https://github.com/Arrow-kb/FS25_RealisticWeather/pull/170)** — a swapped
  `self`/`superFunc` parameter order that would have crashed on every savegame load
  ("attempt to call a table value"), proven by comparing against the codebase's own established calling
  convention rather than guessing.
- **[AutoDrive#544](https://github.com/Stephan-S/FS25_AutoDrive/pull/544)** — read the discussion before the
  code: the maintainers had already flagged the change as reintroducing a deliberately-fixed regression.
  Backed their call with a concrete alternative instead of repeating what was already said.
- **[ContractBoost#122](https://github.com/GMNGjoy/FS25_ContractBoost/pull/122)** — a likely nil-crash when
  opening a UI menu for a disabled game feature.
- **[ContractBoost#115](https://github.com/GMNGjoy/FS25_ContractBoost/pull/115)** — a hardcoded engine
  constant for a new DLC feature that nobody had verified against the base game.

## 🚜 Farming Simulator 25 — mods & server tooling

My proving ground: a real dedicated server, real multiplayer, real players hitting real bugs.
Multiplayer is where sloppy code actually breaks — which makes it honest training for the security work.

- **[FS25_IronHorseRealism](https://github.com/KeilerHirsch/FS25_IronHorseRealism)**
  Original modular vehicle-realism framework for FS25.
- **[FS25_16xMapFix](https://github.com/KeilerHirsch/FS25_16xMapFix)**
  Diagnosis + verified fix for the 16x-map "freezes at 100% compiling shaders" bug.
- **[FS25_AutoVRAMOptimizer](https://github.com/KeilerHirsch/FS25_AutoVRAMOptimizer)**
  Raises the texture-streaming VRAM budget automatically, matched to your card.
- **[FS25_NoResetMP](https://github.com/KeilerHirsch/FS25_NoResetMP)**
  Hardcore multiplayer: disables the free vehicle "reset to shop".
- **[FS25_SoundOverhaulRealism](https://github.com/KeilerHirsch/FS25_SoundOverhaulRealism)**
  Engine-accurate vehicle sounds (I6/V8), built strictly from CC0 / self-recorded audio.
- **[fs25-server-watch](https://github.com/KeilerHirsch/fs25-server-watch)**
  Zero-dependency dedicated-server monitor: live status, joins, crashes.

## ⚖️ Consumer rights

- **[reach-a-human](https://github.com/KeilerHirsch/reach-a-human)**
  Bypasses AI customer-service bots to reach a real human, and documents how to exercise GDPR/CCPA rights
  when a company hides behind automation.

## 🔍 Security research

I hunt bugs in code I actually run — game mods, AI tooling, agent CLIs — and report them as tested patches,
not drive-by issues. Concrete and recent:

- **A recurring multiplayer vulnerability class, found across 5 independent FS25 mod authors**: a
  server-authoritative network event missing the origin check its sibling events correctly have, letting a
  modified client spoof a fake "server message" straight at the server and overwrite protected state. 7 issues
  filed — economy exploits (forged invoices, unlimited money, forged crop quality in
  [MoistureSystem](https://github.com/Ozz-Modding/FS25_MoistureSystem/issues/63)), a cross-farm exploit with
  a crash vector in [EnhancedAnimalSystem](https://github.com/Chissel/FS25_EnhancedAnimalSystem/issues/45),
  and an unbounded-read DoS.
- **A server-freeze + fail-open farm-authorization bug** in a Farming Simulator mod: reported, fixed, and
  credited by name twice in the maintainer's own release notes.
- **A dedicated-server crash** and a **data-loss bug** in two other mods — root-caused by bisection against
  live server and client logs, then submitted as PRs.
- **Upstream fixes** to the AI memory system I depend on, found by running it under real load rather than
  reading its source.

Coordinated disclosure only. No public details before a fix ships — and I don't claim other people's CVEs.

## ⚙️ How I work

Every repo here clears the same floor, because "works on my machine" is not a standard:

- **CI on every push** — lint and tests, so the green badge means something
- **An explicit license** — no license means all rights reserved, which helps nobody
- **Tests before the release**, not after the bug report
- **Adversarial review before shipping** — a second pass whose only job is to find what I missed
- **Root cause over band-aid** — hypothesis → reproduction → evidence → fix. No "this should help" commits.
- **Measure, never guess** — a claim without a number is a hunch wearing a lab coat.

---

<div align="center">

📫 **Open an issue on any repo above** — that's the reliable way to reach me.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-FF5E5B?style=flat&logo=kofi&logoColor=white)](https://ko-fi.com/keilerhirsch)

</div>
