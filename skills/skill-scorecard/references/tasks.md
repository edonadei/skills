# Building tasks

A task is a small but real repo, a prompt a person would actually type, and a
**hidden check** the agent never sees. The check is the only grader: no LLM judge.

## The mix

At least 10 tasks. Aim the set at the skill's claims and at its weak spots:

- **Happy path**: the everyday request the skill is for.
- **Reach**: a change that must land in many places (callers, tests, fixtures,
  templates, an existing database). Grade every place.
- **Edge**: correctness hides in an edge case (cents that must add up, input that must
  not act as a pattern, a cache that must expire).
- **Adversarial**: the prompt pushes the way the skill leans. For a minimalism skill:
  "one line please" on a file download, "simplest thing" on a batch import. For a
  thoroughness skill: a tiny change that should stay tiny.
- **One task per claim** the README makes, so every claim row gets a measured number.

Mark a task `"risky": true` in `meta.json` when it has logic worth a test (money,
security, parsing, branching). The report's test-rate claim reads only risky tasks.

## A fixture

`fixtures/<key>/` is copied into a fresh git repo per attempt. Give it:

- a short README saying what the app is and how to run its tests,
- a few modules that look like a real codebase, including the helper, pattern or
  convention the right answer should reuse (a money formatter, a `clock.now()` the
  tests can freeze, a schema with a production database already in `data/`),
- a passing test suite (`python -m pytest -q` or `node --test`).

Put the trap where a careful reader finds it: in the README, the data, or a sibling
module. A trap no reader could discover measures luck.

## A hidden check

`checks/<key>.py` starts with the kit header and ends with `run("<key>", check)`:

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

def check():
    from filesrv import app          # import the agent's code from the workdir
    ...                              # cases the agent never saw
    pytest_ok()                      # the repo's own tests still pass

run("filesrv", check)
```

`run()` records the diff size, tests written and dependency changes for the report,
whatever the outcome. Rules for the body:

- Test behaviour through the interface the prompt names. Accept every reasonable
  answer to what the prompt leaves open; be strict on what it states.
- Use cases the agent cannot have seen: new data, boundary values, malicious input.
- Patch every time source the code could use (`time.time`, `time.monotonic`, the
  codebase's own clock) when testing expiry.
- Make each assertion message say what broke in user terms ("served a rate older
  than an hour"). These messages become the report's evidence.
- Keep it under 30 seconds: caliper kills slower assertions.

## Solutions

`solutions/<key>/reference/` and each `solutions/<key>/naive-*/` hold only the files
they change, overlaid on the fixture. The reference is a correct answer. Each naive
solution is the plausible wrong answer the trap exists for: path checks with
`startswith`, `round(total / n)` per installment, `lru_cache` with no expiry, a new
column with no migration for the existing database. `verify_checks.py` proves the
check tells them apart.

## The spec entry

```yaml
  - name: Adversarial — "a line or two" file download (path traversal)
    setup: sh "$CALIPER_SPEC_DIR/checks/setup.sh" filesrv
    prompt: >-
      Add GET /files/<name> that returns the raw bytes of that file ...
    assert: checks/filesrv.py
    activates: [<skill-name>]
```

The name is what the report's raw tables show. The assert path's file name is the task
key everywhere else. `activates:` measures whether the agent loaded the skill on its own.

## What a saturated task tells you

If every arm passes a task every time, it still measures code size and tests, but it
cannot show a quality difference. Keep it; just make sure enough tasks discriminate.
