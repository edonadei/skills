# Skills For Your Skills

Your agent is carrying dozens of installed skills right now. Almost none of them
run. All of them cost context on every turn, and nothing on your machine will
tell you which ones are dead.

These skills audit the rest of your skills. What is installed, what has ever
fired, what it costs you per message, and what you can safely throw away.

## Installation (30-second setup)

Skills install as ordinary files you own and can edit. Nothing updates behind
your back, and you pull changes when you want them.

<details>
<summary><strong>Claude Code, Codex, and other agents</strong></summary>

```bash
npx skills@latest add edonadei/skills
```

The installer asks which skills you want and which agents to install them on.
Take all of them: the pack is small on purpose.

</details>

<details>
<summary><strong>Updating</strong></summary>

```bash
npx skills update
```

Pulls the latest version of anything you installed from here.

</details>

<details>
<summary><strong>Running the audit without installing anything</strong></summary>

Clone it and run the script directly. It has no dependencies beyond Node.

```bash
git clone https://github.com/edonadei/skills
node skills/skills/aggressively-cleanup-skills/scripts/audit.mjs
```

It only reads. Nothing is moved or deleted unless you run the archive step
yourself.

</details>

### Then ask your agent

```text
Which of my skills do I actually use?
```

## The pack

| Skill | What it does |
|---|---|
| [`aggressively-cleanup-skills`](./skills/aggressively-cleanup-skills/SKILL.md) | Audits every skill on your machine, reports which are dead and why, archives the ones you confirm. |
| [`harness-infographic`](./skills/harness-infographic/SKILL.md) | Turns a claim about AI tooling or evals into a fact-checked chart card for X, and tells you when a post is not worth publishing. |

More coming.

## Why These Skills Exist

### #1: You Are Paying Rent On Skills You Never Use

**The problem.** Every installed skill puts its name and description in front of
the model on every single turn, whether or not it ever gets chosen. Install
enough of them and you are spending thousands of tokens before you type a word.

Three numbers, all measured on one working developer's machine:

- **77 skills installed**, arriving in three bulk actions. Barely any were
  chosen one at a time.
- **~5,900 tokens** of descriptions loaded before a single word gets typed.
- **4 skills** ever activated on their own across six weeks of transcripts.

Everything else was rent.

**The fix** is [`aggressively-cleanup-skills`](./skills/aggressively-cleanup-skills/SKILL.md).
It reads your session transcripts, works out what has genuinely fired, and shows
you the cost of what has not.

### #2: Nobody Tells You When A Skill Dies

**The problem.** Skill authors retire things. They move a skill to `deprecated/`
or leave it half-finished in `in-progress/`, and your installer copies it onto
your machine without a word. Months later it is still there, still costing you
tokens, still doing nothing.

On the same machine, twelve installed skills came from folders their own author
had marked as dead or unfinished.

**The fix** is the same audit. It reads the installer's lock file, sees the
upstream path each skill came from, and tells you which ones the author already
gave up on.

> [!TIP]
> Every verdict names its reason and shows the evidence. That is the difference
> between a tool you can act on and a list of names you delete blindly.

### #3: Deleting Skills Is Scary

**The problem.** Cleanup tools that delete are tools you run once, nervously,
and never again.

**The fix** is that nothing here deletes. Skills get archived: real directories
move whole, symlinks get repointed to absolute targets and re-checked, and a
`RESTORE.md` lands beside them with one-line restore commands. Emptying the
archive is your job.

## Related

[Caliper](https://github.com/edonadei/caliper) measures whether one skill you are
building works: does it fire, does it beat the bare agent, did your last edit
break it. This pack points the other way, at everything already installed and
whether it deserves to stay.

## Licence

MIT
