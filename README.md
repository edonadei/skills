# skills

Agent skills I use and maintain. Each one is a folder of plain files you
install into Claude Code, Codex, or any agent that supports skills, and you can
edit them like any other file.

## Install

```bash
npx skills@latest add edonadei/skills
```

The installer asks which skills you want and which agents to install them on.
Nothing updates on its own. To pull changes:

```bash
npx skills update
```

## Skills

| Skill | What it does |
|---|---|
| [`aggressively-cleanup-skills`](./skills/aggressively-cleanup-skills/SKILL.md) | Finds the installed skills you never use and archives the ones you confirm. |
| [`harness-infographic`](./skills/harness-infographic/SKILL.md) | Turns a claim about AI tooling or evals into a fact-checked chart for X. |

### aggressively-cleanup-skills

Every installed skill puts its name and description in the model's context on
every turn, whether or not it is ever used. On my machine that was 77 skills
and about 5,900 tokens per message. In six weeks of transcripts, the agent had
picked only 4 of them on its own. Twelve had come from folders their author had
already marked as deprecated or unfinished.

The skill reads your session transcripts and the installer's lock file, works
out which skills have actually run, and lists the rest with the reason for each.
It only removes what you confirm, and it archives instead of deleting:
directories are moved, symlinks are repointed, and a `RESTORE.md` says how to
undo each one.

To run the audit without installing anything (it only reads):

```bash
git clone https://github.com/edonadei/skills
node skills/skills/aggressively-cleanup-skills/scripts/audit.mjs
```

Or ask your agent:

```text
Which of my skills do I actually use?
```

### harness-infographic

Turns a post or claim about agents, harnesses, evals, routers, or model cost
into a chart card for X. It checks the claim first, on a token budget you pick,
and only numbers it can trace to a source go on the card. It also tells you
when a post would add nothing to the one you are replying to.

```text
Make a card for this post, standard budget: https://x.com/...
```

## Related

[Caliper](https://github.com/edonadei/caliper) tests a single skill you are
building: whether it triggers, whether it does better than the agent without
it, and whether your last change broke it.

## Licence

MIT
