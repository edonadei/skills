# Hill-climbing skill-scorecard

An eval for `skills/skill-scorecard`, built to compare two candidate versions per round.

## The tasks

Each one targets a stage of the skill where a weak version fails visibly. All four are
graded by hidden checks in `checks/`; the last also has an LLM-judged `expect`.

| Task | Fixture | Passes when |
|---|---|---|
| Design a scorecard (steps 1-3) | `safe-sql`, a small skill with a SessionStart hook | the skill is pinned, the 3 README claims are listed, `inject.sh` prints the hook's output, 3 tasks pass `verify_checks.py`, prompts don't leak the grading, a check sends an injection payload, and `forbidden_files` can't flag a fixture's own files |
| Report a finished run (steps 6-7) | the real ponytail run | the claims show the summary's numbers (−38% code, −2% tokens, −10% time, 53% vs 46% tests), the verdict is MIXED, slide 3 shows the two flipped tasks, no headline percentage is invented, and all 4 slides stay inside their margins |
| Report a harmful skill (steps 6-7) | ponytail's run with the always-on arm made worse | the verdict is BAD, "More tasks solved" is marked not reproduced, 47% vs 92% appears, and a loss is shown |
| Smoke run with an expired login (step 4) | every attempt an auth `infra_error` | no new runs are started, and the reply blames the login, calls them infrastructure errors, hands `/login` to the user, and holds step 5 |

A stub `caliper` on the agent's PATH refuses `caliper run`, so no task can start billed runs.

## A round

```bash
rm -rf candidates/A candidates/B
cp -R ../../skills/skill-scorecard candidates/A   # then edit A
cp -R ../../skills/skill-scorecard candidates/B   # then edit B differently
sh run.sh 2 r1 A B
```

`run.sh` writes `results/<tag>-<candidate>.{json,log}`. Compare the two runs with
`caliper compare results/r1-A.json results/r1-B.json`, read the failures, and copy the
winner back into `skills/skill-scorecard`.

To rebuild the fixtures from a finished ponytail scorecard folder:
`python3 build_fixtures.py <ponytail-eval-dir>`.
