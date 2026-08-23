# aggressively-cleanup-skills — domain glossary

A glossary only: canonical terms and their meanings. No implementation details,
no specs. Decisions live in `docs/adr/`.

## Installed skill

One skill present on the machine and visible to an agent. The unit this tool
audits. Its *content* may live elsewhere: on a machine using the skills CLI,
`~/.claude/skills/<name>` is usually a **symlink** into `~/.agents/skills/<name>`,
and a real directory only when an older installer copied it. Both shapes are
installed skills; the difference matters only to [[archive]], which must repoint
a symlink rather than carry it.

Deliberately *not* called a neighbourhood: caliper uses "skill neighbourhood"
for the set an eval spec declares, which is a measurement construct and a
different thing. User-facing text says **your installed skills**.
_Avoid_: neighbourhood, inventory.

## Reachability

Whether an agent can choose an [[installed skill]] on its own. A skill carrying
`disable-model-invocation: true` is **summon-only**: it can never activate, and
the only route to it is a human typing its name. Everything else is
**auto-capable**.

Reachability is not the same as **presence**: on the machines observed so far,
most summon-only skills never appear in the agent's context at all, so they cost
nothing per turn — but some do appear. Presence is therefore measured, never
inferred from the flag.
_Avoid_: enabled, active.

## Invocation

One recorded instance of a skill being used, from session transcripts. Three
routes, and the distinction is the whole point:

- **Summoned** — the human typed the skill's name.
- **Chained** — another skill's body told the agent to call it, so the human
  started it indirectly.
- **Autonomous** — the agent chose it with no summon behind it.

A skill with zero invocations of any route is **untouched**. Untouched is the
evidence for [[reason]] 2, and it is only meaningful once the skill is old
enough to have had a chance (see [[eligibility]]).

## Reason

Why the tool believes a skill should go. Six, and every verdict names exactly
one plus the evidence behind it. The reason is the product: a list of names is
what a person deletes blindly.

1. **Retired upstream** — the author moved it to `deprecated/` or `in-progress/`.
2. **Untouched** — zero [[invocation|invocations]], any route, since install.
3. **Never summoned** — summon-only, and the human has never typed it.
4. **Duplicate** — its description overlaps a skill that *is* used.
5. **Invisible** — never appears in the agent's context, so it can never fire.
6. **Undescribed** — no usable `description`, so nothing can ever choose it.

## Tier

How strong a [[reason]]'s evidence is. Aggression belongs in how *widely* the
tool looks, never in how confidently it asserts.

- **Provable** — the machine states it as fact (reasons 1, 6).
- **Strong** — measured over adequate history (reasons 2, 5).
- **Circumstantial** — a judgement call the human should check (reason 4).
- **Clutter** — proven as hard as provable, but the skill never reaches the
  agent's context, so removing it shortens the slash menu and saves no tokens
  (reason 3).

Only **provable** is pre-selected for removal. Clutter grades *payoff* where the
other three grade *evidence*, which is why it sits apart rather than inside
provable: a bucket whose removals change no number belongs where nobody expects
one.

## Eligibility

Whether a skill has existed long enough to be judged **untouched**. A skill
installed yesterday has not failed at anything. Under the minimum age it is
reported as *too new to judge* and no usage-based [[reason]] may attach to it.

The same guard covers a machine with no transcripts: with no usable history,
usage-based reasons are **switched off for the whole run** and the report says
so. Missing evidence must never read as evidence of disuse.

## Archive

Removal, made reversible. A skill leaves the agent's discovery path but nothing
is destroyed: a real directory is moved whole, a symlink is repointed to an
**absolute** target and re-verified. Relative symlink targets break silently
when moved a level deeper, which is why the move is always followed by a
resolve check.

Deletion is never performed. The archive folder is the human's to delete.

## Keep-list

Skills the human has explicitly declined to remove. Still audited and still
counted in the token total, but reported collapsed, so a second run is not a
repeat of the first. A skill defended repeatedly and never used is its own
finding.
