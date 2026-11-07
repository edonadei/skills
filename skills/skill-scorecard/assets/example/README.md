# Example: ponytail

The evaluation this skill was built from (ponytail @ 16352ac, Claude Sonnet 5.5, 12
tasks, 342 graded runs). Copy its shapes:

- `meta.json` and `copy.json`: the real run's task list and report wording.
- `inject.sh`: prints what ponytail's Claude Code plugin injects at session start,
  using the plugin's own hook code (vendored in the original eval folder).
- `fixtures/filesrv`, `checks/filesrv.py`, `solutions/filesrv/`: one complete task, a
  file download under "a line or two" pressure, with a path-traversal trap and two
  naive solutions the check must catch.

Only `filesrv` is included, so `verify_checks.py` here reports the other 11 tasks as
missing solutions.
