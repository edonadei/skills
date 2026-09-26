---
name: harness-infographic
description: Turn a claim, benchmark, tip, or someone's post about AI tooling — coding harnesses (Claude Code, Codex, Cursor: skills, CLAUDE.md/AGENTS.md, hooks, subagents, MCP), agent frameworks, routers, evals and LLM-as-a-judge, eval tools (Caliper, LangSmith, Braintrust…), new models and decision models (e.g. Jev), benchmarks, cost/latency — into a fact-checked, data-first X post: chart cards (PNG) rendered from verified numbers, a short thread, alt text, and a sources post. Fact-checking runs first on an explicit token budget (quick / standard / deep) and gates what goes on the graphic; no verified data, no card; and a value check decides whether the post is worth publishing at all. Also use it to scan the user's X timeline for claims worth a data post. Use this whenever the user wants to share, amplify, quote, rebut, or respond to something about AI tooling or evals on X/Twitter, asks for an infographic, chart, visual, card, or thread for a post, asks which posts on their timeline are worth a chart, or says "someone said something great about X, make a visual" — even if they don't say "infographic", "chart", or "fact-check".
---

# Data-first AI-tooling posts

Goal: the user wants to amplify and argue about ideas in AI tooling and evals on X without ever posting something wrong or empty. Their credibility is the asset: a pretty graphic with a false claim, or a thread that is only commentary on someone else's chart, costs more than no post. So the fact-check comes first and gates the design, and a value check decides whether to post at all.

Three rules shape everything below:
1. **Every card shows data** — a chart of verified numbers, or one sourced headline number. Text-only cards don't go out.
2. **The chart is the argument, the text is its caption.** A short thread (the format Crémieux, @cremieuxrecueil, uses): the chart in the very first post, then one chart per post walking through the evidence, naming the dataset each time.
3. **Add something the source doesn't have.** Original data beats a comparison nobody ran, which beats a clearer replot, which beats commentary. An evals person is credible when they bring numbers, not opinions about other people's numbers.

Work in a folder: `~/infographics/<YYYY-MM-DD>-<slug>/`. Everything the skill produces lands there.

## 0. Finding a candidate (when the user asks what to post about)

Read the user's timeline in the browser (their home feed needs them signed in; X shows logged-out visitors only a handful of posts, so ask them to sign in themselves — never enter their password). Only read: no likes, reposts, or follows. Collect ~50–60 posts, then keep the ones that make a **checkable claim with numbers** in the user's niche (evals, harnesses, agents, routers, model cost/latency). Rank by: data available to verify or reproduce, fit with the user's expertise, reach of the original post, freshness (a launch is worth reacting to within ~2 days). Flag and usually skip rumours/leaks (nothing to verify). Present a short ranked table with the reason for each, then the recommended pick and the angle.

## 1. Intake

The input is usually one of: a post URL (read it in the browser; if X hides it logged-out, ask the user to paste the text), pasted text or a screenshot, a paper/blog/benchmark link, or the user's own draft or eval result. Open the post's images too — the numbers are often only in a chart screenshot.

Pull out **atomic claims**: one checkable statement each. Separate:
- **Factual claims** about a tool/model — checkable against docs, changelogs, source.
- **Empirical claims** (numbers, "X% better") — need the original measurement, or a reproduction. These are where the chart comes from.
- **Opinions** — not fact-checked, but they must be attributed, never presented as fact.

Check who the author is: if they build, sell, or are paid by the thing they're praising (founder, employee, investor, partner that sells it), say so in the post text ("@x, CEO of Y, …") — praise from the maker isn't independent evidence. Benchmark numbers a vendor publishes about its own product can be charted if verified, but the provenance line says "vendor numbers".

If a post is from someone else, record their handle and the exact wording. Paraphrase and credit them; never put words in quotes they didn't write.

## 2. Fact-check and find the data, on a budget

Ask the user for the budget if they didn't give one; default to **standard**. The budget exists so the user decides how much to spend on verification up front, and the report at the end shows what was actually spent.

| Budget | Verification | Data | Rough cost |
|---|---|---|---|
| **quick** | One primary source per factual claim. Empirical claims marked "unverified — author's number". | Only numbers already published in a primary source (paper, benchmark repo, official blog, docs). | ~10–20k tokens |
| **standard** | Primary source + one independent confirmation per claim; check source dates against the tool's current version; look for known caveats (version, plan, OS, flag, dataset). Also look for what the source *doesn't* report (baselines, costs, benchmark names, error bars) — check the vendor's earlier posts and public repos before claiming something is missing. | Published numbers, traced to the original table/figure (not a blog's retelling); plus a cheap reproduction if one takes minutes. | ~30–60k tokens |
| **deep** | Standard, plus an adversarial pass by a fresh subagent (it hasn't seen your reasoning, so it doesn't inherit your bias — give it only the claims and the method, and ask it to find reasons each is wrong or unfair). | Your own measurement: a small Caliper eval, a benchmark run, a timing/cost run. **Read `references/measurement.md` first** — it covers budget protection, confounds, and how to get the numbers out. | ~80–200k tokens + any API spend |

Treat the adversarial subagent's report as leads, not facts: verify each factual point it makes yourself before it changes the post (it can be right about the gist and wrong on details).

Source priority: official docs/changelogs and the source code; the paper or benchmark repo with raw results; then reputable practitioners. Blog posts, press, and other tweets are corroboration, not proof — numbers get mangled in retelling, so always trace a number back to the table it came from. AI tooling changes monthly: note the date/version of every source.

Give each claim a verdict:
- ✅ **Verified** — primary source says so.
- 🟡 **Partly / with caveat** — true under conditions. The caveat goes on the graphic (a few words) or the claim gets reworded.
- ❓ **Unverified** — can appear only as attributed opinion in the post text, never as fact, never charted.
- ❌ **False / outdated** — not used.

Before any comparative wording ("pricier than the others", "the fastest"), check it against *every* item in the comparison, not just the ones you looked at first.

For every number you intend to chart, record its **provenance**: exact value, unit, n, how it was measured, source link + table/figure, date.

Write `factcheck.md`: one row per claim (verdict, corrected wording, source URL + date), a **Data** section with the provenance of every charted number, corrections you made along the way, and the budget used (tier, searches/fetches, subagent tokens from the Agent completion notice, and any API money spent).

**Gates:**
- Core claim ❌ → stop and show the fact-check. A correction can itself be a good post; offer it.
- **No verifiable data** → stop before designing. Say what's missing and propose the cheapest way to get it, with a cost; let the user choose.

## 3. Value check — is this worth posting?

Before designing, write one line per planned card: *what does this add that the original post doesn't?* Be honest:
- **Original data** (your own run, a comparison nobody published) → strong.
- **A clearer replot that changes the reading** (e.g. a relative "+82%" shown as absolute 56% vs 31% on a 0–100 scale) → modest.
- **A replot of a chart the source already shows clearly** → near zero; drop the card.
- **Commentary, asks, or an inconclusive partial run** → weak, and it can read as armchair criticism.

If most of the thread is modest-or-weak, say so plainly and recommend the smaller move — a single reply with one card under the original post, or not posting — plus what data would make it worth a full thread and what it would cost. The user decides; don't polish a thread you'd advise against.

## 4. Plan the thread

A sequence of claims, one chart each — usually 1–4 cards, only as many as there is verified, valuable data:
1. **First card** — the most important verified finding; it must stand alone.
2. **Evidence cards** (optional) — the breakdown, a second dataset, the robustness check, the comparison people will ask about.
3. **Caveat** — where the result doesn't hold, if it matters (a card if there's data, otherwise a line in the text).

The last post of the thread is text: the sources.

**Chart titles say plainly what is shown** — either a descriptive title ("Agent tasks solved by Jev Router and Auto Router") or a flat statement of the finding ("81% of Jev Router's spend went to one model"). Write like a figure caption in a paper: no rhetorical questions, teasers, or framing ("82% more than what?", "the baseline this chart is missing", "Credit where due") — that reads as AI-written. The title says exactly what the data shows, nothing stronger, and fits on two lines; don't repeat numbers the bars already show if that makes it run long.

## 5. Design

Before drawing any chart, load the `dataviz` skill and follow it (form choice, color, anti-patterns). What follows is specific to these cards.

Read `assets/template.html`. The look is light and neutral: white card on a pale gray background, serif title (Newsreader) with a small accent square, one-line gray subtitle naming the metric and "Higher/Lower is better", dashed gridlines, vertical bars with the value printed above each. Keep that look; don't reintroduce dark or decorative themes. The default card is `layout-chart`: title + subtitle + `.chart` + provenance (+ a short caveat) + footer. Optional layouts (`layout-stat` for one sourced number, `layout-list`, `layout-compare`) exist but are rarely right.

The `.chart` block is built from `.bar` rows — edit the numbers, not the heights:
- `data-value` (raw number) and `data-label` (shown text); `hi` on the one bar the post is about (charcoal), the rest stay gray. If every bar is equally the subject, mark them all `hi`.
- `data-max="100"` for percentages so 56% looks like 56%, with `data-unit="%"` to label the gridlines.
- An empty `data-value` renders a missing data point ("not reported") — use it to show a comparison that should exist but wasn't published.
- For trends or distributions, build inline SVG following `dataviz`, with the same tokens.

Rules that make it work on X:
- **1080×1350** (4:5, biggest in the mobile feed).
- Readable on a phone: title ≥ 64px, labels ≥ 26px, ≤ ~30 words outside the chart. Cut words, don't shrink fonts.
- Only: title, subtitle, chart, provenance line, a caveat of a few words if required, and the footer. No kicker, no narration ("I ran it myself…"), no personal handle, no affiliation line — context goes in the post text, right above the image.
- One claim, one chart, one unit per card; bars start at zero; say the direction; label every bar; no legend for one series.
- **Provenance line under every chart:** `n=… · method · source, date` (e.g. `n=423 tasks · 4 unnamed agent benchmarks · OpenRouter runs, Sep 2026 · vendor numbers`).
- Footer: only the data credit (`data: @OpenRouter · Jev by @typesafeai`, `data: my OpenRouter key`).
- Every number and word on the card matches `factcheck.md`.

Copy the template to the work folder as `card-1.html`, `card-2.html`, …

## 6. Render and QA

```bash
node ~/.claude/skills/harness-infographic/scripts/render.mjs card-1.html card-1.png 1080 1350
```

(Headless Chrome/Edge via the DevTools protocol at 2× scale; no dependencies; warns if text overflows. Set `CHROME_PATH` if it can't find a browser.)

Open each PNG with the Read tool and check it like a stranger scrolling on a phone: the finding lands in 2 seconds from the chart alone, bar heights match the numbers, no orphaned title words or colliding labels, provenance legible, nothing contradicts `factcheck.md`. Fix and re-render until it passes.

## 7. Deliver

Send the PNGs, then give in chat:
1. **The value check** — one line per card, and your recommendation (thread, single reply, or don't post).
2. **Thread text** — same plain, scientific voice as the cards: state the numbers and what they do and don't show; no rhetorical questions, hype, or "gotcha" framing. ≤ 280 chars per post (a link counts as 23). Links only in the last post.
3. **What to quote** — the specific post that makes the claim you're charting (the one with the vendor's chart), not the marketing repost and not necessarily the thread opener; quote it so readers see the original next to your card. Optionally suggest a one-card reply under the highest-reach post in that thread. Tag the parties whose numbers you use.
4. **Alt text** per card — the title and every value, in full sentences.
5. **Fact-check summary** — verdict per claim, corrections made, budget spent (tokens and any API money).

Never post, reply, or DM on the user's behalf; hand over the assets and let them publish.
