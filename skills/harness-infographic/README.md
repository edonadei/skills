# harness-infographic

Posting about AI tooling is easy. Posting something that is true, and that adds
anything to the post you are replying to, is not.

This turns a claim about agents, harnesses, evals, routers, or model cost into a
chart card for X. It fact-checks first, on a token budget you pick, and only
verified numbers make it onto the card. Then it asks whether the post is worth
publishing at all, and tells you when it is not.

## Install

```bash
npx skills@latest add edonadei/skills
```

Rendering needs Node and an installed Chrome or Edge. Nothing else.

```bash
node scripts/render.mjs card.html card.png 1080 1350
```

## Use it

Ask your agent:

```text
Which posts on my timeline make a claim worth a chart?
```

```text
Make a card for this post, standard budget: https://x.com/...
```

You get a work folder with:

- `factcheck.md`: a verdict per claim, where every charted number came from, and
  what the check cost
- `card-1.png` and friends: 1080×1350, light and neutral, one chart per card
- thread text, alt text, and which post to quote, in the chat

## Budgets

| Budget | What it buys | Rough cost |
|---|---|---|
| quick | one primary source per claim | ~10–20k tokens |
| standard | a primary source plus an independent confirmation, and a look for what the source left out | ~30–60k tokens |
| deep | standard, plus a fresh subagent trying to break the claims, plus your own measurement | ~80–200k tokens, plus any API spend |

Deep runs can spend real money. `references/measurement.md` covers how to keep
that bounded: pilot every configuration, checkpoint results, and watch spend
while the run is going, not after.

## What it will refuse to do

- Put a number on a card that it could not trace back to a source
- Make a text-only card
- Post, reply, or DM for you
- Type your API key or password
