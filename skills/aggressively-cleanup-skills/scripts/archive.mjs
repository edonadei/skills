#!/usr/bin/env node
// Archive skills out of the agent's discovery path. Reversible by construction:
// a real directory moves whole, a symlink is repointed to an ABSOLUTE target and
// re-verified. Nothing is ever deleted. See references/evidence.md.
//
//   node scripts/archive.mjs --tier provable
//   node scripts/archive.mjs --skill review --skill obsidian-vault
//   node scripts/archive.mjs --tier strong --dry-run
//   node scripts/archive.mjs --keep research        # decline, add to keep-list

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const HOME = os.homedir();
const OUTDIR = process.env.SKILL_AUDIT_DIR ?? path.join(os.homedir(), '.skill-audit');
const AUDIT = path.join(OUTDIR, 'audit.json');
const KEEPLIST = path.join(OUTDIR, 'keep-list.json');

const argv = process.argv.slice(2);
const flag = name => argv.filter((a, i) => argv[i - 1] === `--${name}`);
const has = name => argv.includes(`--${name}`);

if (!fs.existsSync(AUDIT)) {
  console.error(`no ${AUDIT}. Run: node scripts/audit.mjs`);
  process.exit(1);
}
const audit = JSON.parse(fs.readFileSync(AUDIT, 'utf8'));

// --- keep-list ---------------------------------------------------------------

const keepList = fs.existsSync(KEEPLIST)
  ? JSON.parse(fs.readFileSync(KEEPLIST, 'utf8'))
  : { declined: {} };

const declines = flag('keep');
if (declines.length) {
  for (const name of declines) keepList.declined[name] = new Date().toISOString();
  fs.mkdirSync(OUTDIR, { recursive: true });
  fs.writeFileSync(KEEPLIST, JSON.stringify(keepList, null, 2));
  console.log(`kept: ${declines.join(', ')}`);
  if (!flag('tier').length && !flag('skill').length) process.exit(0);
}

// --- selection ---------------------------------------------------------------

const tiers = flag('tier');
const named = flag('skill');
const dryRun = has('dry-run');

let selected = audit.skills.filter(s =>
  (tiers.length && tiers.includes(s.tier)) || named.includes(s.name));

const blocked = selected.filter(s => !s.removable);
selected = selected.filter(s => s.removable && !keepList.declined[s.name]);

if (!selected.length && !blocked.length) {
  console.error('nothing selected. Pass --tier provable|strong|circumstantial or --skill <name>');
  process.exit(1);
}

for (const s of blocked)
  console.log(`skipped  ${s.name}: ${s.rootKind}-provided, uninstall the ${s.rootKind} instead`);

// --- archive -----------------------------------------------------------------

const stamp = new Date().toISOString().slice(0, 10);
const label = tiers.length ? tiers.join('-') : 'selected';
const dest = path.join(HOME, '.claude/skills-archive', `${label}-${stamp}`);

if (dryRun) {
  console.log(`\ndry run, would archive ${selected.length} skills to ${dest}`);
  for (const s of selected) console.log(`   ${s.name}  (${s.evidence})`);
  process.exit(0);
}

fs.mkdirSync(dest, { recursive: true });
const moved = [];
const failed = [];

for (const s of selected) {
  const to = path.join(dest, s.name);
  try {
    if (s.isSymlink) {
      // Relative targets break when moved deeper. Resolve, then relink absolute.
      const resolved = fs.realpathSync(s.dir);
      fs.unlinkSync(s.dir);
      fs.symlinkSync(resolved, to);
    } else {
      fs.renameSync(s.dir, to);
    }
    // Verify from the new location before claiming success.
    fs.statSync(path.join(to, 'SKILL.md'));
    moved.push(s);
  } catch (err) {
    failed.push({ name: s.name, error: err.message });
  }
}

fs.writeFileSync(path.join(dest, 'RESTORE.md'), `# Archived ${stamp}

${moved.length} skills removed from the agent's discovery path. Nothing was
deleted: real directories were moved whole, symlinks were repointed to absolute
targets in \`~/.agents/skills\`.

${moved.map(s => `- **${s.name}** — ${s.evidence}`).join('\n')}

## Restore everything

\`\`\`bash
for s in ${dest}/*/; do
  n=$(basename "$s")
  [ -L "$s" ] && ln -s "$(readlink "$s")" ~/.claude/skills/$n || mv "$s" ~/.claude/skills/
done
\`\`\`

## Restore one

\`\`\`bash
mv ${dest}/<name> ~/.claude/skills/
\`\`\`

Deleting this folder is your call. This tool will not do it.
`);

const saved = moved.reduce((a, s) => a + s.tokens, 0);
console.log(`\narchived ${moved.length} skills to ${dest}`);
console.log(`~${saved} tokens per message reclaimed`);
console.log(`~${audit.totals.tokensPerMessage - saved} tokens per message remaining`);
for (const f of failed) console.log(`FAILED   ${f.name}: ${f.error}`);
if (failed.length) process.exitCode = 1;
