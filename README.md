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
| [`skill-scorecard`](./skills/skill-scorecard/SKILL.md) | Measures whether a skill makes the agent better, and publishes the report and images for X. |

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

### skill-scorecard

Runs the same model on the same realistic tasks without a skill, with it installed,
and with it always on, then grades every attempt with hidden checks the agent never
sees. It publishes a report page and 4 images for an X post, and says so plainly when
a skill changes nothing or makes things worse.

```text
/skill-scorecard https://github.com/DietrichGebert/ponytail
```

## Related

[Caliper](https://github.com/edonadei/caliper) tests a single skill you are
building: whether it triggers, whether it does better than the agent without
it, and whether your last change broke it.

## Licence

MIT
