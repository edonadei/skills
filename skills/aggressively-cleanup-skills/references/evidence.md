# Evidence

Where the audit looks, and how each verdict is proven. Read this when the script
reports a root it could not parse, or when someone asks how a verdict was
reached.

## Skill roots

Only **discovery roots** count: places an agent actually looks for skills.

| Path | Kind | Removable |
|---|---|---|
| `~/.claude/skills` | user | yes |
| `~/.claude/plugins` | plugin | no, uninstall the plugin |
| `./.claude/skills` | project | yes, but shared with a team |

`~/.agents/skills` is a **content store**, not a discovery root. The skills CLI
symlinks out of it into `~/.claude/skills`. Counting it resurrects every skill
the user has already archived, so it stays out of the list.

## Two traversal traps

A skill directory is usually a **symlink**. `readdirSync(dir, {withFileTypes:
true})` reports a symlinked directory as `isDirectory() === false`, so an
ordinary walk silently skips most of a real machine's skills. Stat through the
link.

Those symlinks often carry **relative** targets (`../../.agents/skills/<name>`).
Moving one a level deeper breaks it without error. Any move must repoint to an
absolute target and then verify the link resolves.

## Transcripts

| Agent | Path |
|---|---|
| Claude Code | `~/.claude/projects/**/*.jsonl` |
| Codex | `~/.codex/sessions/**/*.jsonl` |
| Hermes | `~/.hermes/sessions/**/*.jsonl` |
| pi | `~/.pi/agent/**/*.jsonl` |

One JSON object per line. The two records that matter:

- A **summon** is a `user` record containing
  `<command-name>/name</command-name>`. That is how a typed slash command lands
  in the transcript.
- An **invocation** is an `assistant` record with a `tool_use` block whose
  `name` is `Skill`, reading `input.skill`.

If a root exists but yields no parseable records, say so in the report rather
than treating it as an absence of usage.

## Routes

A skill can be invoked three ways, and the split changes what a zero means.

- **Summoned**: the human typed it.
- **Chained**: another skill's body called it, so a human started it indirectly.
- **Autonomous**: the agent chose it with no summon behind it.

Chaining is detected by proximity: a Skill call within 25 records of a summon is
attributed to that summon. This is a heuristic and it is wrong at the edges.

Two ways to keep it honest. Summon-only skills are a **free control group**: they
cannot activate, so any autonomous count against one is a known false positive
and measures the classifier's own error rate. And the better method, when a
skill's body names the skills it delegates to, is to build the delegation graph
and attribute from that instead of from distance.

## Proving each reason

| Reason | Proof |
|---|---|
| Retired upstream | `skillPath` in `~/.agents/.skill-lock.json` contains `deprecated/` or `in-progress/` |
| Untouched | zero invocations of any route, and the skill is older than the minimum age |
| Never summoned | frontmatter has `disable-model-invocation: true`, and zero summons |
| Duplicate | description overlaps a skill with invocations, above a similarity threshold |
| Invisible | the skill never appears in a captured context listing |
| Undescribed | no `description`, or shorter than 15 characters |

## Token cost

A listing entry is priced as `- <name>: <description>`, at four characters per
token. Approximate by construction, so report it as approximate. It counts the
description only. A skill that actually loads pulls its whole body on top.

## What presence means

Reachability and presence are different. A skill without
`disable-model-invocation` is **reachable**: the agent may choose it. Whether it
is **present** in the agent's context on a given turn is a separate fact, and on
observed machines most summon-only skills never appear at all, so they cost
nothing per turn. Some do appear.

Presence is therefore measured from a captured listing, never inferred from the
flag. Where no listing has been captured, the `invisible` reason is unavailable
and the report says so.
