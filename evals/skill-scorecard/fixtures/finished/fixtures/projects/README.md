# projects

Project tracker backend (SQLite). HTTP entry point: `projects/api.py::handle`.
Production data lives in `data/projects.db` (`connect("data/projects.db")`); a copy is checked in for local dev.
Run tests with `python -m pytest -q`.
