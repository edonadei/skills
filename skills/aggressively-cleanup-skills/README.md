# aggressively-cleanup-skills

Finds the installed skills you never use and archives the ones you confirm.
Unused skills still cost tokens on every message, because each one's name and
description is loaded whether or not it runs.

## Install

```bash
npx skills@latest add edonadei/skills
```

Or run the scripts from a clone. They need only Node, and the audit only reads.

```bash
node scripts/audit.mjs
node scripts/report.mjs
```

The audit prints a summary (skills installed, tokens per message, how much
transcript history it read) and writes `audit.json`. The report turns that into
an HTML page: the token cost, which skills have run and which never have, and
each verdict with its evidence.

## Use

Ask your agent:

```text
Which of my skills do I actually use?
```

## Reasons

Each flagged skill gets one reason, and the report shows the evidence for it.

| Reason | Evidence |
|---|---|
| Retired upstream | the author moved it to `deprecated/` or `in-progress/` |
| Undescribed | no usable description, so the agent can't choose it |
| Untouched | never used by any route since it was installed |
| Invisible | it never reaches the agent's context, so it can't run |
| Duplicate | its description overlaps a skill you do use |
| Never summoned | it can't activate on its own, and you have never typed it |

## Tiers

Verdicts are grouped by how strong the evidence is:

- **Provable** (retired upstream, undescribed): stated as fact. Pre-selected
  for removal.
- **Strong** (untouched, invisible): measured over enough history to mean
  something.
- **Circumstantial** (duplicate): a judgement call, worth checking yourself.
- **Clutter** (never summoned): these skills only load when typed, so removing
  them shortens your slash menu rather than saving tokens. Never pre-selected.

Skills installed less than 14 days ago are marked too new to judge. If there
are no usable transcripts, the usage-based reasons are turned off for the whole
run and the report says so, so a machine with no history doesn't look like a
machine full of dead skills.

## Removal

Nothing is deleted. A real directory is moved whole, a symlink is repointed to
an absolute target and checked again, and a `RESTORE.md` next to them lists
how to undo each one. Emptying the archive is up to you.

Plugin and bundled skills are counted in the cost but can't be removed this
way. The report names the plugin to uninstall instead.

## How it works

It reads each skill's frontmatter, the installer's lock file, and your agent's
session transcripts, then counts the tokens in every description. On 272
transcript files (48k records) it runs in under half a second.

Two details that are easy to get wrong: `~/.agents/skills` is a content store,
not a place the agent discovers skills from, so counting it brings back skills
you already archived. And a symlinked skill directory reports
`isDirectory() === false`, so a plain directory walk misses most of the skills
on a real machine.

Terms are defined in [`docs/CONTEXT.md`](docs/CONTEXT.md).
