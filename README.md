# edonadei/skills

Skills for auditing your skills.

Your agent is probably carrying dozens of installed skills right now. Almost
none of them run. All of them cost context on every turn, and nothing on your
machine will tell you which ones are dead.

This pack is the tooling for that: measuring what your installed skills actually
do, and getting rid of the ones that do nothing.

## Install

```bash
npx skills@latest add edonadei/skills
```

## The pack

| Skill | What it does |
|---|---|
| [`aggressively-cleanup-skills`](skills/aggressively-cleanup-skills) | Audits every skill installed on your machine, reports which are dead and why, and archives the ones you confirm. |

More coming. Same idea behind each of them: nobody audits their installed
skills, and it shows up on the bill every message.

## Why this exists

Three numbers, all measured on one developer's machine:

- **77 skills installed**, and they arrived in three bulk actions. Barely any
  were chosen one at a time.
- **~5,900 tokens** of skill descriptions loaded before a single word gets typed.
- **4 skills** ever activated on their own across six weeks of transcripts.

Everything else was rent.

## Related

[Caliper](https://github.com/edonadei/caliper) measures whether one skill you
are building works: does it fire, does it beat the bare agent, did your last
edit break it. This pack points the other way, at everything already installed
and whether it deserves to stay.

## Licence

MIT
