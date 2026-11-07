#!/bin/sh
# Run candidates on this eval, in parallel. Usage: sh run.sh <k> <tag> <candidate> [candidate ...]
# Candidates live in candidates/<name>/ (a full copy of the skill folder).
set -e
K=$1; TAG=$2; shift 2
M=${MODEL:-claude-code:claude-sonnet-5-5}
SHIM="$PWD/.shimhome"; rm -rf "$SHIM"; mkdir -p "$SHIM"
for f in Library .nvm .pyenv .gitconfig .npm; do [ -e "$HOME/$f" ] && ln -s "$HOME/$f" "$SHIM/$f"; done
cp "$HOME/.claude.json" "$SHIM/.claude.json"
mkdir -p results
for NAME in "$@"; do
  sed "s/__NAME__/$NAME/g" scorecard.eval.yaml.in > "spec-$NAME.eval.yaml"
  HOME=$SHIM SC_CANDIDATE="$PWD/candidates/$NAME" caliper run "spec-$NAME.eval.yaml" --k "$K" --timeout 2700 \
    --workers 4 --fail-fast 2 -m "$M" --output "results/$TAG-$NAME.json" > "results/$TAG-$NAME.log" 2>&1 &
done
wait
for NAME in "$@"; do echo "== $NAME"; grep -E "Score|unusable" "results/$TAG-$NAME.log" || true; done
