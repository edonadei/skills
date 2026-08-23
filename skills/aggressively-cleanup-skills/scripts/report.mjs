#!/usr/bin/env node
// Render .cleanup/audit.json as a standalone HTML report: the cost split and
// the fired-versus-never grid up top, the verdicts and their evidence below.
// Zero dependencies. See references/evidence.md for what the evidence means.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const OUTDIR = process.env.SKILL_AUDIT_DIR ?? path.join(os.homedir(), '.skill-audit');
const AUDIT = path.join(OUTDIR, 'audit.json');
const OUT = path.join(OUTDIR, 'report.html');

if (!fs.existsSync(AUDIT)) {
  console.error(`no ${AUDIT}. Run: node scripts/audit.mjs`);
  process.exit(1);
}
const a = JSON.parse(fs.readFileSync(AUDIT, 'utf8'));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const fired = a.skills.filter(s => {
  const i = s.invocations || {};
  return (i.summoned + i.chained + i.autonomous) > 0;
});
const flagged = a.skills.filter(s => s.reason);
const tooNew = a.skills.filter(s => s.tooNew);
const keptTokens = a.totals.tokensPerMessage - a.totals.reclaimableTokens;

const TIERS = [
  ['provable', 'The machine states these as fact.'],
  ['strong', 'Measured over enough history to mean something.'],
  ['circumstantial', 'A judgement call. Check these yourself.'],
];

const cells = a.skills.map(s => {
  const i = s.invocations || {};
  const on = (i.summoned + i.chained + i.autonomous) > 0;
  return `<span class="d ${on ? 'on' : s.summonOnly ? 'summon' : 'off'}" title="${esc(s.name)}"></span>`;
}).join('');

const tierSections = TIERS.map(([tier, blurb]) => {
  const rows = flagged.filter(s => s.tier === tier)
    .sort((x, y) => y.tokens - x.tokens);
  if (!rows.length) return '';
  const sum = rows.reduce((t, s) => t + (s.costsContext ? s.tokens : 0), 0);
  const clutter = rows.filter(s => !s.costsContext).length;
  return `<section>
  <h2>${tier} <span class="muted">${rows.length} skills, ~${sum} tokens/message${
    clutter ? ` (${clutter} cost nothing)` : ''}</span></h2>
  <p class="blurb">${blurb}</p>
  <table><thead><tr><th>Skill</th><th>Why</th><th class="n">Tokens</th></tr></thead><tbody>
  ${rows.map(s => `<tr><td><code>${esc(s.name)}</code>${s.removable ? '' :
      ` <span class="tag">${esc(s.rootKind)}</span>`}</td><td>${esc(s.evidence)}</td>
      <td class="n">${s.costsContext ? s.tokens
        : '<span class="free" title="never reaches the agent&#39;s context">clutter</span>'}</td></tr>`).join('')}
  </tbody></table>
</section>`;
}).join('');

const html = `<title>Skill audit</title>
<style>
:root{--surface:#fcfcfb;--plane:#f4f3ef;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--hair:#e1e0d9;--off:#c9c7bf;--on:#2a78d6;--warn:#8a6410}
*{box-sizing:border-box}
body{margin:0;padding:26px 18px 48px;background:var(--plane);color:var(--ink);
font-family:ui-sans-serif,-apple-system,"Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
.card{max-width:900px;margin:0 auto;background:var(--surface);border:1px solid var(--hair);
border-radius:12px;padding:40px 42px 34px}
h1{font-size:clamp(25px,3.6vw,34px);line-height:1.15;letter-spacing:-.024em;margin:0 0 10px;font-weight:690}
h1 em{font-style:normal;color:var(--on);font-variant-numeric:tabular-nums}
.sub{color:var(--ink2);margin:0 0 30px;font-size:15.5px;line-height:1.5}
.bar{display:flex;gap:2px;height:52px;margin-bottom:10px}
.bar div{border-radius:3px}
.bar .waste{background:var(--off)}
.bar .keep{background:var(--on)}
.axis{display:flex;gap:2px;font-size:12.5px;color:var(--ink2);margin-bottom:30px}
.axis b{display:block;color:var(--ink);font-variant-numeric:tabular-nums}
.grid{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.d{width:12px;height:12px;border-radius:50%}
.d.on{background:var(--on)}
.d.off{box-shadow:inset 0 0 0 1.5px var(--off)}
.d.summon{box-shadow:inset 0 0 0 1.5px var(--hair)}
.legend{font-size:12.5px;color:var(--muted);margin:0 0 34px}
section{border-top:1px solid var(--hair);padding-top:22px;margin-top:26px}
h2{font-size:18px;margin:0 0 4px;font-weight:660;text-transform:capitalize}
h2 .muted{font-weight:400;font-size:13px;color:var(--muted);text-transform:none}
.blurb{color:var(--ink2);font-size:14px;margin:0 0 14px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
padding:0 0 8px;border-bottom:1px solid var(--hair);font-weight:600}
td{padding:10px 0;border-bottom:1px solid var(--hair);vertical-align:baseline}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
code{background:#eef2f7;padding:1px 5px;border-radius:3px;font-size:13px}
.tag{font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--warn);
border:1px solid var(--warn);border-radius:2px;padding:1px 5px}
.free{color:var(--muted);font-size:12px;font-variant-numeric:normal}
.note{margin-top:26px;font-size:12.5px;line-height:1.55;color:var(--muted)}
</style>
<div class="card">
<h1>${a.totals.skills} skills cost you <em>~${a.totals.tokensPerMessage}</em> tokens on every message. <em>${a.totals.flagged}</em> of them look dead.</h1>
<p class="sub">Every verdict below names one reason and shows its evidence.
Archiving is reversible and nothing is ever deleted.${a.totals.clutterSkills
  ? ` ${a.totals.clutterSkills} of them are marked <em>clutter</em>: summon-only skills that
      never reach the agent's context, so removing them tidies your slash menu
      rather than saving tokens.` : ''}</p>

<div class="bar">
  <div class="waste" style="flex:${a.totals.reclaimableTokens || 1}"></div>
  <div class="keep" style="flex:${keptTokens || 1}"></div>
</div>
<div class="axis">
  <div style="flex:${a.totals.reclaimableTokens || 1}"><b>~${a.totals.reclaimableTokens}</b>reclaimable</div>
  <div style="flex:${keptTokens || 1}"><b>~${keptTokens}</b>earning their place</div>
</div>

<div class="grid">${cells}</div>
<p class="legend">One dot per skill. Filled means it has been invoked at least
once (${fired.length} of ${a.totals.skills}). Hollow means never. Faint means it
cannot activate at all.</p>

${tierSections || '<section><h2>Nothing flagged</h2><p class="blurb">No skill met any removal reason.</p></section>'}

<p class="note">
${a.usage.usable
  ? `Usage measured across ${a.usage.transcriptFiles} transcript files, ${a.usage.records} records, ${a.usage.historyDays} days of history.`
  : `<strong>No usable transcripts were found, so every usage-based reason is switched off for this run.</strong> Only metadata reasons appear above.`}
${tooNew.length ? ` ${tooNew.length} skills are newer than the minimum age and were not judged on usage.` : ''}
Token counts are estimated at four characters per token and cover descriptions
only. A further ~${a.totals.uncountedTokens} tokens sit in summon-only descriptions and are
excluded, because those mostly never reach the agent's context.
Generated ${esc(a.generatedAt)}.
</p>
</div>`;

fs.writeFileSync(OUT, html);
console.log(`wrote ${OUT}`);
console.log(`${a.totals.flagged} flagged, ~${a.totals.reclaimableTokens} tokens/message reclaimable`);
