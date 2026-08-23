# aggressively-cleanup-skills

Most of the skills on your machine have never run once. They still cost you
tokens on every message you send.

This audits every installed skill, tells you which ones are dead and why they
are dead, then archives whatever you confirm. It never deletes anything.

## Install

```bash
npx skills@latest add edonadei/skills
```

Or run the script straight from a clone. It has no dependencies beyond Node, and
it only reads.

```bash
node scripts/audit.mjs
```

## Use it

Ask your agent:

```text
Which of my skills do I actually use?
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

Every verdict names one reason and shows the evidence behind it. That is the
part that matters. Hand someone a bare list of names and all they can do is
delete blindly.

| Reason | Evidence |
|---|---|
| Retired upstream | the author moved it to `deprecated/` or `in-progress/` |
| Untouched | zero invocations, any route, since it was installed |
| Never summoned | it cannot activate, and you have never typed it |
| Duplicate | its description overlaps a skill you do use |
| Invisible | it never reaches the agent's context, so it can never fire |
| Undescribed | no usable description, so nothing can choose it |

## Three tiers

Some evidence is much better than other evidence, so verdicts are graded. The
aggression is in how widely the audit looks. It stays honest about how sure it
is.

- **Provable**: the machine states it as fact. Pre-selected for removal.
- **Strong**: measured over enough history to mean something.
- **Circumstantial**: a judgement call, and you should check it.

## Two guards

A skill you installed yesterday has not failed at anything. Anything under 14
days old comes back as *too new to judge*.

If there are no usable transcripts, every usage-based reason switches off for
the whole run and the report says so on its face. Otherwise a machine with no
history would look like a machine full of dead skills.

## Removal is reversible

A real directory gets moved whole. A symlink gets repointed to an absolute
target and then re-checked. A `RESTORE.md` lands next to them. Emptying the
archive is your job, and this tool will not do it for you.

Plugin and bundled skills get audited for cost but cannot be removed this way,
so the report tells you which plugin to uninstall instead.

## How it works

Node, no dependencies. It reads skill frontmatter, the installer lock file and
your agent's session transcripts, then prices every description in tokens. On
272 transcript files and 48k records it finishes in under half a second.

Two things it gets right that a first attempt usually gets wrong. `~/.agents/skills`
is a content store rather than a discovery root, so counting it resurrects
skills you already archived. And a symlinked skill directory reports
`isDirectory() === false`, which hides most of a real machine's skills from an
ordinary directory walk.

Terms are defined in [`docs/CONTEXT.md`](docs/CONTEXT.md).
