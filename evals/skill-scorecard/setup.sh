#!/bin/sh
# Prepare an attempt's workdir.
#   setup.sh target           ./target-skill: the safe-sql skill as a git repo
#   setup.sh scorecard <fix>  ./scorecard: the candidate's kit, then fixtures/<fix> on top
set -e
case "$1" in
  target)
    cp -R "$CALIPER_SPEC_DIR/fixtures/safe-sql" target-skill
    git -C target-skill init -q && git -C target-skill add -A
    git -C target-skill -c user.name=dev -c user.email=dev@example.com commit -qm "safe-sql 1.0" ;;
  scorecard)
    mkdir -p scorecard
    cp -R "$SC_CANDIDATE/assets/kit/." scorecard/
    cp -R "$CALIPER_SPEC_DIR/fixtures/$2/." scorecard/ ;;
esac
