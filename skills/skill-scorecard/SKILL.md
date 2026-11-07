---
name: skill-scorecard
description: Run a full Caliper evaluation of an agent skill on realistic tasks, publish the report, and render 4 images for X.
disable-model-invocation: true
---

Measure what a skill really does: the same model on the same realistic tasks, with
and without the skill, graded by **hidden checks**. The output is a **scorecard**:
a published report page and 4 images for an X post. Every number on both traces to
the pooled summary JSON. If the skill is useless or harmful, the scorecard says so.

Inputs: the skill (a path or a GitHub URL), the model (default `claude-sonnet-5-5`).
Needs `caliper` (`pipx install caliper-eval`), Python 3 with `pytest` and `pyyaml`,
Node, Chrome, and Playwright for Python.

`<kit>` below is `assets/kit/` in this skill's folder. `assets/example/` is a finished
eval of the ponytail skill: one complete task, plus the `meta.json`, `copy.json` and
`inject.sh` of the real run. Copy its shapes.

## 1. Pin the skill

Make the eval folder `~/scorecards/<YYYY-MM-DD>-<skill>/`. Clone the skill's repo,
note the commit, copy its `SKILL.md` into the eval folder, and copy `<kit>/.` in.
Write `meta.json` (`skill_name`, `skill_repo`, `skill_path`, `commit`, `model`,
`tasks: {}`).

Done when the eval folder holds `SKILL.md`, the kit, and a `meta.json` with the commit.

## 2. List the claims and the real install

Read the skill and its README. Every number or promise the author makes becomes a
**claim** row (claim, what the author says, measured = to fill) in `report/copy.json`.

Find how people actually install it. If the real install injects context on its own
(a plugin hook, a rules file, `AGENTS.md`), write `inject.sh` to print exactly that
context, using the skill's own code at the pinned commit where it has any. That is the
**always-on arm**. If the skill only ships as a plain skill, skip `inject.sh` and run
two arms.

Done when every claim in the README has a row, and `inject.sh` (if any) prints the
injected text when run from a fixture folder.

## 3. Build the tasks

Read [references/tasks.md](references/tasks.md), then build at least 10 tasks. Each
one gets `fixtures/<key>/`, `checks/<key>.py`, `solutions/<key>/reference/`, at least
one `solutions/<key>/naive-*/`, a `meta.json` entry and a spec entry in
`scorecard.eval.yaml`.

Done when `python3 verify_checks.py` prints `ALL CHECKS VERIFIED`: every check fails
on the untouched fixture, passes the reference, and fails every naive solution.

## 4. Smoke run

`caliper validate scorecard.eval.yaml`, then `sh run-arms.sh 1 k1`. Read every
failure's evidence. A harness error (auth, usage limit, a false `cheat`) is fixed
before going further: [references/running.md](references/running.md) lists the known
ones.

Done when every arm has 0 unusable attempts and each task failure's evidence is a real
defect in the agent's code.

## 5. Measure

Run rounds (`sh run-arms.sh 5 r1`, `sh run-arms.sh 5 r2`, …) and pool them with
`python3 aggregate.py r1 r2 …`. Top up short tasks with a spec holding only those
tasks (see running.md).

Done when `aggregate.py` shows `min n/task` ≥ 8 in every arm, unusable attempts are
excluded, and at least two tasks are failed at least once by some arm. If every task
passes everywhere, the eval is saturated: add harder tasks and go back to step 3.

## 6. Report

Read [references/report.md](references/report.md). Fill `report/copy.json` from the
pooled summary, run `python3 report/build.py summary-<tags>.json`, look at the page
once, and publish `report/scorecard.html` as an Artifact.

Done when the page is published and every number in `copy.json` has been checked
against the summary JSON.

## 7. Images for X

Fill the `slides` block of `copy.json`, run
`python3 report/render_slides.py summary-<tags>.json`, and open every PNG.

Done when the script prints `ok` for all 4 slides and you have looked at each image.

## 8. Deliver

Give the user the page link (it is private until they share it), the 4 images in
order, alt text for each, and a draft post whose every number matches the images.
State the caveats: model, sample size, and any README claim measured on a different
model. Never post on the user's behalf.
