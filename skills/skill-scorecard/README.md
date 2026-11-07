# skill-scorecard

Measures whether an agent skill makes the agent better, then publishes the result: a
report page and 4 images for an X post.

The same model runs the same realistic tasks three ways: without the skill, with the
skill installed (the agent decides whether to load it), and with the skill always on
(the way its real installer loads it). Hidden checks grade every attempt by running the
agent's code on cases it never saw. No LLM judge.

Each check is verified before any agent runs: it must fail on the untouched repo, pass a
reference solution, and fail the plausible wrong answer it exists to catch.

## Install

```bash
npx skills@latest add edonadei/skills
```

It needs [Caliper](https://github.com/edonadei/caliper) (`pipx install caliper-eval`),
Python 3 with `pytest` and Playwright, Node, and Chrome. To iterate on the images'
design, it points to the [impeccable](https://github.com/pbakaus/impeccable) skill
(`npx impeccable install`).

## Use

It runs only when you call it, since a full evaluation takes hours and a few hundred
agent runs:

```text
/skill-scorecard https://github.com/DietrichGebert/ponytail
```

## What you get

- `~/scorecards/<date>-<skill>/`: the tasks, the hidden checks, every raw result.
- A report page: pass rates with confidence intervals, code written, tokens and time,
  how often the agent loaded the skill on its own, every attempt as a dot, and the
  author's claims next to the measured numbers.
- 4 images at 6:5, the shape X shows uncropped in a multi-image post. Every mark on
  them is one real graded run: the code each run wrote, the runs where the agent loaded
  the skill, and the runs on the tasks that flipped.

`assets/example/` is the ponytail evaluation this skill was built from: 12 tasks,
342 graded runs on Claude Sonnet 5.5.

## Evaluating this skill

`evals/skill-scorecard/` at the root of this repo holds Caliper tasks for this skill
itself, built to compare two candidate versions of it per round.
