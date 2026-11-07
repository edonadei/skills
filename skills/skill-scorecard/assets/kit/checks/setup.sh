#!/bin/sh
# Copy a fixture repo into the attempt workdir and commit it as the pristine root.
# SC_INJECT=1 (the "always-on" arm): run the eval's inject.sh, which prints the context
# the skill's real install would inject (e.g. a plugin's SessionStart hook output); it is
# placed where Claude Code loads project context.
set -e
cp -R "$CALIPER_SPEC_DIR/fixtures/$1/." .
printf '__pycache__/\n.pytest_cache/\nnode_modules/\n' > .gitignore
if [ "$SC_INJECT" = 1 ]; then
  mkdir -p .claude
  sh "$CALIPER_SPEC_DIR/inject.sh" > .claude/CLAUDE.md
fi
git init -q
git add -A
git -c user.name=dev -c user.email=dev@example.com commit -qm "initial import"
