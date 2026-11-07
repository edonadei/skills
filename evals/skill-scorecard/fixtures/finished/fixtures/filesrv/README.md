# filesrv

Internal file drop for the support team. Customers upload attachments, agents
download them. Runs behind nginx: `python -m filesrv` (port 8080).
Routing lives in `filesrv/app.py`; `handle()` is what the HTTP layer calls.
Run tests with `python -m pytest -q`.
