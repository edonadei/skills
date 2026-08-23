#!/usr/bin/env node
// Audit every installed agent skill. Zero dependencies, Node stdlib only.
//
// Terms used here are defined in docs/CONTEXT.md: reason, tier, eligibility,
// invocation (summoned / chained / autonomous), reachability, presence.

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const HOME = os.homedir();
const MIN_AGE_DAYS = 14;          // eligibility: below this, too new to judge
const CHAIN_WINDOW = 25;          // records after a summon that count as chained
const CHARS_PER_TOKEN = 4;        // rough, and reported as approximate

// --- where things live -------------------------------------------------------

const SKILL_ROOTS = [
  // Discovery roots only. ~/.agents/skills is a content store the CLI symlinks
  // *into* ~/.claude/skills; counting it would resurrect archived skills.
  { kind: 'user',    dir: path.join(HOME, '.claude/skills'),  removable: true },
  { kind: 'plugin',  dir: path.join(HOME, '.claude/plugins'), removable: false },
  { kind: 'project', dir: path.join(process.cwd(), '.claude/skills'), removable: true },
];

const TRANSCRIPT_ROOTS = [
  path.join(HOME, '.claude/projects'),
  path.join(HOME, '.codex/sessions'),
  path.join(HOME, '.hermes/sessions'),
  path.join(HOME, '.pi/agent'),
];

const LOCK_FILES = [path.join(HOME, '.agents/.skill-lock.json')];

// --- small helpers -----------------------------------------------------------

const exists = p => { try { fs.statSync(p); return true; } catch { return false; } };
const readJSON = p => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
const days = ms => Math.floor((Date.now() - ms) / 86400000);

function walkFiles(dir, match, out = [], depth = 0) {
  if (depth > 6 || !exists(dir)) return out;
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    // A symlinked skill dir reports isDirectory() === false, so stat through it.
    let isDir = e.isDirectory();
    if (!isDir && e.isSymbolicLink()) {
      try { isDir = fs.statSync(p).isDirectory(); } catch { isDir = false; }
    }
    if (isDir) walkFiles(p, match, out, depth + 1);
    else if (match(e.name)) out.push(p);
  }
  return out;
}

function frontmatter(text) {
  const m = /^---\n([\s\S]*?)\n---/.exec(text);
  if (!m) return {};
  const fm = m[1];
  const grab = key => {
    const r = new RegExp(`^${key}:\\s*(.+(?:\\n\\s+.+)*)`, 'm').exec(fm);
    return r ? r[1].replace(/\s+/g, ' ').trim().replace(/^["'|>]+|["']+$/g, '') : '';
  };
  return {
    name: grab('name'),
    description: grab('description'),
    summonOnly: /^disable-model-invocation:\s*true/m.test(fm),
  };
}

// --- collect installed skills ------------------------------------------------

function collectSkills() {
  const found = new Map();
  for (const root of SKILL_ROOTS) {
    if (!exists(root.dir)) continue;
    for (const file of walkFiles(root.dir, n => n === 'SKILL.md')) {
      const dir = path.dirname(file);
      const fm = frontmatter(fs.readFileSync(file, 'utf8'));
      const name = fm.name || path.basename(dir);
      if (found.has(name)) continue;              // first root wins
      let lst; try { lst = fs.lstatSync(dir); } catch { continue; }
      found.set(name, {
        name,
        dir,
        rootKind: root.kind,
        removable: root.removable,
        isSymlink: lst.isSymbolicLink(),
        linkTarget: lst.isSymbolicLink() ? fs.readlinkSync(dir) : null,
        installedAtMs: lst.birthtimeMs || lst.mtimeMs,
        description: fm.description,
        summonOnly: fm.summonOnly,
        // what a listing entry costs the context window, approximately
        tokens: Math.round(`- ${name}: ${fm.description}`.length / CHARS_PER_TOKEN),
      });
    }
  }
  return [...found.values()];
}

// --- upstream status from the installer lock ---------------------------------

function upstreamStatus() {
  const status = new Map();
  for (const lf of LOCK_FILES) {
    const lock = readJSON(lf);
    const skills = lock?.skills;
    if (!skills) continue;
    for (const [name, meta] of Object.entries(skills)) {
      const folder = /skills\/([^/]+)\//.exec(meta.skillPath || '')?.[1] ?? null;
      status.set(name, {
        folder,
        retired: folder === 'deprecated' || folder === 'in-progress',
        source: meta.source ?? null,
        installedAt: meta.installedAt ?? null,
      });
    }
  }
  return status;
}

// --- invocations from transcripts --------------------------------------------

function countInvocations() {
  const files = TRANSCRIPT_ROOTS.flatMap(r => walkFiles(r, n => n.endsWith('.jsonl')));
  const counts = new Map();   // name -> {summoned, chained, autonomous}
  let records = 0;
  let earliest = Infinity;

  const bump = (name, kind) => {
    const c = counts.get(name) ?? { summoned: 0, chained: 0, autonomous: 0 };
    c[kind]++; counts.set(name, c);
  };

  for (const file of files) {
    let lines;
    try { lines = fs.readFileSync(file, 'utf8').split('\n'); } catch { continue; }
    const recs = [];
    for (const l of lines) {
      if (!l.trim()) continue;
      try { recs.push(JSON.parse(l)); records++; } catch { /* skip */ }
    }
    let lastSummon = -Infinity;
    recs.forEach((d, i) => {
      const ts = Date.parse(d.timestamp ?? '');
      if (ts && ts < earliest) earliest = ts;
      const content = d.message?.content;
      const blocks = Array.isArray(content) ? content : [];
      if (d.type === 'user') {
        const text = typeof content === 'string'
          ? content
          : blocks.map(b => b?.text ?? '').join(' ');
        const cmds = [...String(text).matchAll(/<command-name>\/?([a-z0-9:_-]+)<\/command-name>/g)];
        for (const m of cmds) bump(m[1].split(':').pop(), 'summoned');
        if (cmds.length) lastSummon = i;
      } else if (d.type === 'assistant') {
        for (const b of blocks) {
          if (b?.type !== 'tool_use' || b?.name !== 'Skill') continue;
          const n = b.input?.skill;
          if (!n) continue;
          bump(n.split(':').pop(), i - lastSummon <= CHAIN_WINDOW ? 'chained' : 'autonomous');
        }
      }
    });
  }
  return { counts, records, files: files.length, earliestMs: earliest };
}

// --- verdicts ----------------------------------------------------------------

const TIER = { retired: 'provable', neverSummoned: 'provable', undescribed: 'provable',
               untouched: 'strong', invisible: 'strong', duplicate: 'circumstantial' };

function verdict(skill, up, inv, usageUsable) {
  const total = inv ? inv.summoned + inv.chained + inv.autonomous : 0;
  const age = days(skill.installedAtMs);

  if (up?.retired)
    return { reason: 'retired-upstream', tier: TIER.retired,
             evidence: `author moved it to ${up.folder}/ upstream${up.source ? ` (${up.source})` : ''}` };

  if (!skill.description || skill.description.length < 15)
    return { reason: 'undescribed', tier: TIER.undescribed,
             evidence: 'no usable description, so nothing can ever choose it' };

  if (!usageUsable) return null;                       // no history: usage reasons off
  if (age < MIN_AGE_DAYS)
    return { reason: null, tier: null, tooNew: true,
             evidence: `installed ${age} day${age === 1 ? '' : 's'} ago, too new to judge` };

  if (skill.summonOnly && total === 0)
    return { reason: 'never-summoned', tier: TIER.neverSummoned,
             evidence: `cannot activate, and never typed in ${age} days` };

  if (total === 0)
    return { reason: 'untouched', tier: TIER.untouched,
             evidence: `zero invocations of any route in ${age} days` };

  return null;
}

// --- run ---------------------------------------------------------------------

const skills = collectSkills();
const upstream = upstreamStatus();
const { counts, records, files, earliestMs } = countInvocations();
const usageUsable = records > 0 && files > 0;
const historyDays = Number.isFinite(earliestMs) ? days(earliestMs) : 0;

const rows = skills.map(s => {
  const inv = counts.get(s.name) ?? null;
  const v = verdict(s, upstream.get(s.name), inv, usageUsable);
  return {
    ...s,
    upstream: upstream.get(s.name) ?? null,
    invocations: inv ?? { summoned: 0, chained: 0, autonomous: 0 },
    ageDays: days(s.installedAtMs),
    ...(v ?? { reason: null, tier: null, evidence: null }),
  };
});

const flagged = rows.filter(r => r.reason);
const audit = {
  generatedAt: new Date().toISOString(),
  usage: { usable: usageUsable, transcriptFiles: files, records, historyDays },
  totals: {
    skills: rows.length,
    tokensPerMessage: rows.reduce((a, r) => a + r.tokens, 0),
    flagged: flagged.length,
    reclaimableTokens: flagged.reduce((a, r) => a + r.tokens, 0),
  },
  skills: rows,
};

fs.mkdirSync('.cleanup', { recursive: true });
fs.writeFileSync('.cleanup/audit.json', JSON.stringify(audit, null, 2));

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(audit.totals, null, 2));
} else {
  const t = audit.totals;
  console.log(`${t.skills} skills, ~${t.tokensPerMessage} tokens on every message`);
  if (!usageUsable) console.log('no usable transcripts: usage-based reasons are OFF this run');
  else console.log(`${files} transcript files, ${records} records, ${historyDays} days of history`);
  for (const tier of ['provable', 'strong', 'circumstantial']) {
    const g = flagged.filter(r => r.tier === tier);
    if (!g.length) continue;
    console.log(`\n${tier} — ${g.length} skills, ~${g.reduce((a, r) => a + r.tokens, 0)} tokens`);
    for (const r of g.sort((a, b) => b.tokens - a.tokens))
      console.log(`   ${String(r.tokens).padStart(4)}  ${r.name.padEnd(30)} ${r.evidence}`);
  }
  console.log('\nwrote .cleanup/audit.json');
}
