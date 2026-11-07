#!/bin/sh
# Run the three arms in parallel on one spec. Usage (from the eval dir):
#   sh run-arms.sh <k> <tag> [spec]        MODEL=claude-code:<model> overrides the model.
# Arms: noskill (skill ablated), skill (installed, agent chooses),
#       always (installed + inject.sh context, like a plugin that also ships the skill).
set -e
K=$1; TAG=$2; SPEC=${3:-scorecard.eval.yaml}
M=${MODEL:-claude-code:claude-sonnet-5-5}
SKILL=$(python3 -c "import json;print(json.load(open('meta.json'))['skill_name'])")
C=$(command -v caliper)

# Caliper copies ~/.claude/.credentials.json into each attempt's isolated HOME when it exists,
# and only falls back to the Keychain when it doesn't. A stale file breaks every attempt, so
# run under a shim HOME without it. Rebuilt every run: temp dirs get pruned.
SHIM="$PWD/.shimhome"; rm -rf "$SHIM"; mkdir -p "$SHIM"
for f in Library .nvm .pyenv .gitconfig .npm; do [ -e "$HOME/$f" ] && ln -s "$HOME/$f" "$SHIM/$f"; done
cp "$HOME/.claude.json" "$SHIM/.claude.json"

export SC_METRICS="$PWD/metrics-$TAG.jsonl"
COMMON="--k $K --timeout 900 --workers 4 --fail-fast 3 -m $M"
HOME=$SHIM SC_ARM=noskill $C run $SPEC $COMMON --ablate $SKILL --output results-$TAG-noskill.json > run-$TAG-noskill.log 2>&1 &
HOME=$SHIM SC_ARM=skill   $C run $SPEC $COMMON --output results-$TAG-skill.json > run-$TAG-skill.log 2>&1 &
if [ -f inject.sh ]; then
  HOME=$SHIM SC_ARM=always SC_INJECT=1 $C run $SPEC $COMMON --output results-$TAG-always.json > run-$TAG-always.log 2>&1 &
fi
wait
grep -h "Score" run-$TAG-*.log || true
