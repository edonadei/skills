# Running your own measurement (deep tier)

Read this before spending real API credit to produce data. Learned the hard way on 2026-09-26: a Jev Router replication on OpenRouter's public harness spent the whole $3 budget in 13 minutes and saved no solve rates.

## Before you run anything

- **Ask whether the result would be worth posting** (see "Value check" in SKILL.md). Spend only on the comparison that answers the open question — e.g. "router vs always using the model it mostly picks, cost per solved task" — not on a run that can only produce a spend breakdown.
- **Confirm the money budget with the user** and cost the plan with real list prices (`GET https://openrouter.ai/api/v1/models`, no key needed). Per-task token counts come from a pilot, not a guess.
- **API keys: never type, paste, or print one.** The user writes it themselves. For OpenRouter's harness (Bun auto-loads `.env`), give them this PowerShell one-liner — it hides input, stays out of history, and writes UTF-8 without a BOM (a BOM breaks the first line of `.env`):

  ```powershell
  $k = Read-Host "OpenRouter API key" -AsSecureString; $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($k)); [IO.File]::WriteAllText("<harness-dir>\.env", "OPENROUTER_API_KEY=$plain`n", (New-Object Text.UTF8Encoding $false)); Remove-Variable k, plain; "saved"
  ```

  Then run `echo .env >> .git/info/exclude` in that clone so the key can't be committed, and suggest a dedicated key with a credit limit.

## Design the comparison so it can't be dismissed

- **Use the vendor's own public harness when there is one** — nobody can say you rigged the setup. Pin and record the commit.
- **Read the benchmark's real defaults in code, not fallback constants.** In OpenRouter's harness the τ-bench Airline user simulator is `google/gemini-2.5-flash` (`src/benchmarks/benchmark-meta.ts`), not the `USER_FALLBACK_MODEL` in `user-simulator.ts`. Getting this wrong mis-attributes spend.
- **Never use a model under test as the user simulator** (or judge). It confounds the result — the adversarial review caught this.
- **Match conditions or disclose the mismatch.** Routers may pick their own reasoning effort (`jev-router` defaults to adaptive) while fixed models run at the harness default (`high`).
- **Include the model the router actually uses most as a fixed baseline** — you only learn which one that is from a pilot of ~10 tasks. One task is not representative: on 1 easy task Jev Router used GPT-6 Luna + DeepSeek V4.1 Flash for $0.004; on the full run 81% of its spend went to Gemini 3.8 Flash.
- **Sample size:** ~50 tasks × 1 epoch gives roughly ±14 points on a solve rate. Report raw counts and a 95% (Wilson) interval; don't headline gaps smaller than the interval.

## Protect the budget while it runs

1. Run the cheapest, most predictable configurations first (fixed small models), then anything that chooses its own model.
2. **Pilot every configuration on ~10 tasks**, compute cost per task from real billing, project the full run, and only continue if the projection fits.
3. **Checkpoint:** pass `--artifact-dir <dir>` (OpenRouter harness) — it writes its results parquet only at the end, so a run killed by a credit limit otherwise leaves nothing.
4. **Guard spend during the run**, not just between runs: poll `GET https://openrouter.ai/api/v1/key` (`data.usage`, `data.limit_remaining`) every ~30 s from a background loop and kill the run when spend passes its share of the budget. The key's usage figure lags by a minute or so, and in-flight calls can push spend slightly past a hard limit ($3.02 on a $3 cap).
5. The key's credit limit is the last line of defence, not the plan.

## Getting the numbers out

- **Solve rate and harness cost:** `bench-results/*.parquet` (columns include `score_value`, `total_cost`, `input_tokens`, `generation_ids`); read with `hyparquet`, which the harness already depends on.
- **Which model a router actually used, and what was really billed:** the harness doesn't record it. Look up each generation ID with `GET https://openrouter.ai/api/v1/generation?id=<id>` (`model`, `total_cost`) — `scripts/openrouter-costs.ts` does this per run. The harness's own `total_cost` is an estimate.
- **Spend by model for a whole key:** `/api/v1/activity` needs a management key, so ask the user to copy the per-model totals from the key's page in the OpenRouter dashboard.
- **Before comparing prices in a claim** ("X is pricier than the others"), list the price of *every* model involved. Gemini 3.8 Flash is 7–20× Luna/DeepSeek but cheaper than Claude Sonnet 5 and GPT-6 Sol — an early draft got this wrong.

## Windows quirks

- Bun installed via `npm install -g bun` is launched through `bun.cmd`, which refuses JSON arguments (`--solver-config '{"...":"..."}'`). Call the real binary: `"$(npm root -g)/bun/bin/bun.exe" src/cli/index.ts ...`.
- Background runs started from the Bash tool survive `TaskStop` as orphaned `bun.exe` processes only rarely, but check with `Get-Process bun` after stopping one.
