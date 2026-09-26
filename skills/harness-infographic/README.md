# harness-infographic

Turns a claim about AI tooling (agents, harnesses, evals, routers, model cost)
into a chart card for X.

It checks the claim before designing anything, on a token budget you choose.
Only numbers it can trace to a source go on the card. Before building the
thread, it also says what each card adds over the original post, and
recommends a single reply or no post when the answer is "not much".

## Install

```bash
npx skills@latest add edonadei/skills
```

Rendering needs Node and an installed Chrome or Edge:

```bash
node scripts/render.mjs card.html card.png 1080 1350
```

## Use

```text
Which posts on my timeline make a claim worth a chart?
```

```text
Make a card for this post, standard budget: https://x.com/...
```

Each post gets a folder with `factcheck.md` (a verdict per claim and the source
of every charted number) and the cards as 1080×1350 PNGs. The thread text, alt
text, and which post to quote come back in the chat.

## Budgets

| Budget | What it checks | Rough cost |
|---|---|---|
| quick | one primary source per claim | 10–20k tokens |
| standard | a primary source and an independent confirmation, plus what the source left out | 30–60k tokens |
| deep | standard, a second agent trying to disprove the claims, and your own measurement | 80–200k tokens, plus API costs |

Deep runs can spend real money. `references/measurement.md` explains how to
keep them within budget.

It never posts for you, and it never types your API key or password.
