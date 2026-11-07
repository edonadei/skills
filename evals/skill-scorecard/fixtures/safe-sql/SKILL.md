---
name: safe-sql
description: Write SQL that cannot be injected. Use whenever code builds or runs a SQL query.
---

# Safe SQL

Every query takes its values as bound parameters (`?`, `%s`, `:name`), never through
string formatting, f-strings or concatenation.

Identifiers that must vary (a sort column, a table name) come from an allowlist written
in the code; anything else is rejected with an error, not escaped.

`LIKE` searches escape `%`, `_` and the escape character in user input and declare the
escape character with `ESCAPE`.

When fixing one injectable query, grep for the same pattern elsewhere and fix every copy.
