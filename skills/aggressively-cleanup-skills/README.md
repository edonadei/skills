# aggressively-cleanup-skills

Most of the skills on your machine have never run. They still cost you tokens on
every single message.

This audits every installed skill, tells you which are dead **and why**, and
archives the ones you confirm. Nothing is ever deleted.

## Use it

Install the pack, then in your agent:

```text
Which of my skills do I actually use?
```

Or run the audit directly:

```bash
node scripts/audit.mjs
```

```
79 skills, ~5059 tokens on every message
272 transcript files, 47971 records, 335 days of history

provable — 18 skills, ~704 tokens
    107  review                    author moved it to in-progress/ upstream (mattpocock/skills)
     65  to-tickets                cannot activate, and never typed in 44 days
     44  edit-article              cannot activate, and never typed in 64 days

strong — 15 skills, ~630 tokens
     71  codebase-design           zero invocations of any route in 51 days
     63  research                  zero invocations of any route in 44 days
```

## The six reasons

Every verdict names one reason and shows its evidence. The reason is the point:
a bare list is something you delete blindly.

| Reason | Evidence |
|---|---|
| Retired upstream | the author moved it to `deprecated/` or `in-progress/` |
| Untouched | zero invocations, any route, since it was installed |
| Never summoned | it cannot activate, and you have never typed it |
| Duplicate | its description overlaps a skill you *do* use |
| Invisible | it never reaches the agent's context, so it can never fire |
| Undescribed | no usable description, so nothing can choose it |

## Three tiers

Evidence quality varies, so verdicts are graded. Aggression is in how widely it
looks, never in how confidently it asserts.

- **Provable** — the machine states it as fact. Pre-selected for removal.
- **Strong** — measured over adequate history.
- **Circumstantial** — a judgement call you should check.

## Two guards

A skill installed yesterday has not failed at anything, so anything under 14
days is reported as *too new to judge*.

And with no usable transcripts, every usage-based reason is switched **off** for
the whole run, with the report saying so. Missing evidence must never read as
evidence of disuse.

## Removal is reversible

A real directory moves whole; a symlink is repointed to an absolute target and
re-checked. A `RESTORE.md` lands beside them. Deleting the archive is your call,
and this never does it for you.

Plugin-provided and bundled skills are audited for cost but cannot be removed
this way — the report names the plugin to uninstall instead.

## How it works

Node, zero dependencies. It reads skill frontmatter, the installer lock file,
and your agent's session transcripts, then prices each description in tokens.
On 272 transcript files and 48k records it takes under half a second.

Two things it knows that a naive version gets wrong: `~/.agents/skills` is a
content store rather than a discovery root, and a symlinked skill directory
reports `isDirectory() === false`, so most machines' skills are invisible to an
ordinary directory walk.

Terms are defined in [`docs/CONTEXT.md`](docs/CONTEXT.md).
