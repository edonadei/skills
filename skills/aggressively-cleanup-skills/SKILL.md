---
name: aggressively-cleanup-skills
description: Audit every agent skill installed on this machine and remove the dead ones. Use when the user asks which skills they still use, wants to clean up or prune their skills, says they have too many skills, asks what skills are costing them context or tokens, or wants to know why a skill never triggers.
---

Most installed skills never run. They still spend context on every single turn.
This audits what is installed, reports what is dead **and why**, then removes
only what the user confirms.

Work in three phases. Do not merge them: the report exists so the human decides.

## 1. Audit

```bash
node scripts/audit.mjs --json
```

It walks every skills root it can find, reads frontmatter, reads the installer
lock file, counts invocations from session transcripts, and prices each
description in tokens. It writes `~/.skill-audit/audit.json` and prints a summary. Output always goes
there, never to the working directory, because the audit is about the machine
rather than whatever project you happen to be standing in.

Read [`references/evidence.md`](references/evidence.md) when the script reports
a root or transcript format it could not parse, or when the user asks how a
verdict was reached.

Two guards the script enforces, worth restating to the user when they fire:

- A skill under the minimum age is **too new to judge**. It has not failed at
  anything yet.
- With no usable transcripts, usage-based reasons are **off for the whole run**.
  Missing evidence never reads as evidence of disuse.

Done when `audit.json` exists and every installed skill carries either a verdict
or an explicit reason it was not judged.

## 2. Report

```bash
node scripts/report.mjs
```

Writes `~/.skill-audit/report.html`: the token-cost split and the
fired-versus-never grid at the top, then the verdicts grouped by tier, each
showing its reason and raw evidence.

Summon-only skills are shown as **clutter** rather than a token figure. They
mostly never reach the agent's context, so removing them tidies the slash menu
instead of saving tokens. Say that plainly when offering them: a user who
archives twenty of them and sees no token change will not trust the next run.

Offer to publish it as an artifact so the user can share it. Fall back to the
local path.

Then ask which tiers to remove. **Provable** is pre-selected. **Strong**,
**circumstantial** and **clutter** are not.

Clutter is its own bucket for a reason: the proof is as strong as provable, but
the payoff is a shorter slash menu rather than tokens. Offer it separately and
say so, or a user will archive twenty skills and wonder why nothing changed. Name the count and the token saving for each tier in
one line each, and wait.

Done when the user has answered.

## 3. Archive

```bash
node scripts/archive.mjs --tier provable          # or --tier strong, --skill <name>
```

Every removal is reversible. A real directory moves whole; a symlink is
repointed to an absolute target and re-checked. A `RESTORE.md` goes in the
archive folder.

Skills the user declines go to the keep-list and are collapsed on the next run.

Plugin-provided and bundled skills cannot be removed this way. Report them with
the plugin to uninstall instead, and never offer to delete them directly.

Done when every removal resolves from its new location and the recomputed token
total is reported back.

## Reference

- [`references/evidence.md`](references/evidence.md) — where skills and
  transcripts live per agent, and how each reason is proven.
- [`docs/CONTEXT.md`](docs/CONTEXT.md) — the terms: reason, tier, eligibility,
  archive, keep-list.
