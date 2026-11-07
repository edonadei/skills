#!/bin/sh
# Print what ponytail's Claude Code plugin injects at SessionStart (level "full" + codebase map),
# using the plugin's own hook code pinned in vendor/. Runs in the attempt workdir.
V="$CALIPER_SPEC_DIR/vendor/ponytail/hooks"
node -e "process.stdout.write(require('$V/ponytail-instructions.js').getPonytailInstructions('full'))"
printf '\n\n'
node "$V/ponytail-map.js"
