#!/bin/sh
# Prints the rules Claude Code adds to every session's context.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "SAFE-SQL ACTIVE"
echo
sed '1,/^---$/d' "$DIR/SKILL.md"
