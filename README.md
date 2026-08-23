# edonadei/skills

Skills for the skills themselves.

Everyone's agent is now carrying dozens of installed skills. Almost none of them
run. They all cost context on every turn, they collide with each other over the
same prompts, and nothing on your machine will tell you which ones are dead.

This pack is the tooling for that problem: measuring what your skills actually
do, and removing the ones that do nothing.

## Install

```bash
npx skills@latest add edonadei/skills
```

## The pack

| Skill | What it does |
|---|---|
| [`aggressively-cleanup-skills`](skills/aggressively-cleanup-skills) | Audits every skill installed on your machine, reports which are dead and why, and archives the ones you confirm. |

More to come. The through-line is the same: your installed skills are a
dependency tree nobody audits, and it is costing you on every message.

## Why this exists

Three numbers from one developer's machine, measured rather than guessed:

- **77 skills installed**, arriving in three bulk actions. Almost none chosen
  individually.
- **~5,900 tokens** spent on skill descriptions before a single word is typed.
- **4 skills** ever autonomously activated across six weeks of transcripts.

The rest was rent. That is the problem this pack is pointed at.

## Related

[Caliper](https://github.com/edonadei/caliper) measures whether *one* skill you
are building actually works: does it fire, does it beat the bare agent, did your
last edit regress it. This pack is the other direction — everything already
installed, and whether it earns its place.

## Licence

MIT
