// Actual agent-side cost and routed-model mix per run of OpenRouter's benchmark-harness, from the
// generation API (the harness's own total_cost is an estimate; the generation record is what was billed).
// Usage: copy into the harness dir, then: bun.exe openrouter-costs.ts  -> writes ../runs/costs.json and prints a table.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { parquetReadObjects } from "hyparquet";

const H = { Authorization: "Bearer " + process.env.OPENROUTER_API_KEY };
async function gen(id: string) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const res = await fetch("https://openrouter.ai/api/v1/generation?id=" + id, { headers: H });
    if (res.ok) return (await res.json()).data;
    await new Promise((r) => setTimeout(r, 1500 * (attempt + 1))); // records can lag a few seconds
  }
  return undefined;
}

const out: any[] = [];
for (const f of readdirSync("bench-results").filter((f) => f.endsWith(".parquet")).sort()) {
  const b = readFileSync("bench-results/" + f);
  const recs: any[] = await parquetReadObjects({ file: b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) });
  const models: Record<string, number> = {};
  let cost = 0, calls = 0, missing = 0;
  const perTask: { sample: string; solved: boolean; cost: number }[] = [];
  for (const r of recs) {
    let taskCost = 0;
    const ids: string[] = r.generation_ids ? JSON.parse(r.generation_ids) : [];
    // small parallel batches to stay polite to the API
    for (let i = 0; i < ids.length; i += 8) {
      const ds = await Promise.all(ids.slice(i, i + 8).map(gen));
      for (const d of ds) {
        if (!d) { missing++; continue; }
        calls++; taskCost += d.total_cost ?? 0;
        models[d.model] = (models[d.model] ?? 0) + 1;
      }
    }
    cost += taskCost;
    perTask.push({ sample: r.sample_id, solved: Number(r.score_value) >= 1 || r.score_value === "C", cost: taskCost });
  }
  const solved = perTask.filter((t) => t.solved).length;
  const row = { model: recs[0].model, n: recs.length, solved, accuracy: solved / recs.length, agent_cost: cost,
    cost_per_task: cost / recs.length, cost_per_solved: solved ? cost / solved : null, calls, missing, models, perTask };
  out.push(row);
  console.log(`${row.model.padEnd(30)} ${solved}/${row.n} solved (${(100 * row.accuracy).toFixed(1)}%)  agent $${cost.toFixed(4)}  $/solved ${row.cost_per_solved?.toFixed(5)}  calls=${calls} missing=${missing}  ${JSON.stringify(models)}`);
}
writeFileSync("../runs/costs.json", JSON.stringify(out, null, 2));
