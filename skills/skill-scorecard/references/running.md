# Running the arms

`sh run-arms.sh <k> <tag> [spec]` runs every arm in parallel on the same spec and
model (`MODEL=claude-code:<model>` to change it). Each arm writes
`results-<tag>-<arm>.json`, `run-<tag>-<arm>.log`, and one line per graded attempt to
`metrics-<tag>.jsonl`.

| Arm | What the agent has | Answers |
|---|---|---|
| `noskill` | nothing (the skill is ablated) | the baseline |
| `skill` | the skill installed; the agent decides whether to load it | does it fire on its own? |
| `always` | the skill installed plus `inject.sh`'s context in project memory | what it does when it is on |

The `skill` arm's activation rate is a finding in itself: a skill that never fires
changes nothing, however good its body is.

## Sample size

Pool rounds until every task has at least 8 usable attempts per arm. `aggregate.py`
prints `min n/task`, a Wilson interval per arm, a Fisher p for each arm against
`noskill`, and every task that **flipped** (p < 0.05). At n≈10 per task only large
effects show up per task; the pooled pass rate is the headline.

To top up only some tasks, write a second spec holding just those tasks (copy the
entries verbatim, so names and keys match) and run it under a new tag:
`sh run-arms.sh 7 r5 hard.eval.yaml`. `aggregate.py` pools by task key across all specs.

## Known harness errors

- **"Not logged in" or "OAuth token revoked" on every attempt.** Caliper copies
  `~/.claude/.credentials.json` into each attempt's isolated HOME when that file
  exists, and only falls back to the Keychain when it doesn't. A stale file breaks
  everything. `run-arms.sh` runs caliper under a shim HOME without it, rebuilt each
  run. If the Keychain login itself has expired, only the user can fix it: ask them to
  run `claude` and `/login`.
- **"You've hit your … limit" (infra_error).** The account ran out mid-run. Those
  attempts are excluded from every rate, never scored as failures. `--fail-fast 3`
  stops a task after three in a row so the run doesn't burn the rest. Wait for the
  reset, then top up the short tasks.
- **A false `cheat`.** `forbidden_files` patterns match any path the agent touches. A
  bare `fixtures/` pattern also matches a fixture repo's own `fixtures/` folder. Scope
  the patterns to the eval folder's name.
- **"skill './SKILL.md' does not exist."** The eval folder lacks the pinned `SKILL.md`.
- **Timeouts.** Real tasks take minutes; the kit passes `--timeout 900`.

## Before trusting a round

Open one transcript per arm. Check that the `always` arm's reply shows the skill's
behaviour (its signature format, its rules), proving the injection reached the agent.
Check that a failing attempt failed for the reason in its evidence.
