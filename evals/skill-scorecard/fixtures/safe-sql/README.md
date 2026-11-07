# safe-sql

A skill that makes your agent write SQL that cannot be injected.

- **0 injection bugs in 50 agent tasks**, against 14 without the skill.
- **No bigger diffs**: the same lines of code as without it, within 5%.
- Works with `sqlite3`, `psycopg` and SQLAlchemy Core.

## Install

Claude Code plugin: `/plugin install safe-sql`. The plugin's SessionStart hook loads the
rules into every session, so they apply even when the agent does not pick the skill.
