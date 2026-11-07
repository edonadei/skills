"""Shared plumbing for the hidden checks: run a check, record diff metrics, exit 1 on failure.

Each check runs in the attempt workdir (cwd). Setup committed the pristine
fixture as the root commit, so the diff against it is exactly what the agent did.
Metrics go to $SC_METRICS (JSON lines) tagged with $SC_ARM, if set.
"""
import json
import os
import re
import subprocess
import sys
import traceback

WORKDIR = os.getcwd()
sys.path.insert(0, WORKDIR)

TEST_RE = re.compile(r"(^|/)(tests?/|test_[^/]*$|[^/]*_test\.py$|[^/]*\.test\.[cm]?js$)")
DEP_FILES = {"requirements.txt", "package.json", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"}


def sh(*cmd, timeout=20):
    return subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True, timeout=timeout)


def pytest_ok():
    r = sh(sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x")
    assert r.returncode == 0, "existing test suite fails:\n" + (r.stdout + r.stderr)[-800:]


def node_test_ok():
    r = sh("node", "--test")
    assert r.returncode == 0, "node --test fails:\n" + (r.stdout + r.stderr)[-800:]


def _diff_metrics():
    root = sh("git", "rev-list", "--max-parents=0", "HEAD").stdout.split()
    if not root:
        return {"error": "no root commit"}
    sh("git", "add", "-A")
    out = sh("git", "diff", "--cached", "--numstat", root[-1]).stdout
    m = {"src_added": 0, "src_deleted": 0, "test_added": 0, "files_changed": 0,
         "new_files": 0, "dep_files_changed": [], "files": []}
    new = set(sh("git", "diff", "--cached", "--name-only", "--diff-filter=A", root[-1]).stdout.split())
    for line in out.splitlines():
        a, d, path = line.split("\t", 2)
        if a == "-":  # binary
            continue
        a, d = int(a), int(d)
        m["files_changed"] += 1
        m["files"].append(path)
        if path in new:
            m["new_files"] += 1
        if os.path.basename(path) in DEP_FILES:
            m["dep_files_changed"].append(path)
        if TEST_RE.search(path):
            m["test_added"] += a
        elif path.endswith((".py", ".js", ".mjs", ".cjs", ".ts", ".html")):
            m["src_added"] += a
            m["src_deleted"] += d
    patch = sh("git", "diff", "--cached", "-U0", root[-1], "--", ".", ":(exclude)tests", ":(exclude)test").stdout
    m["src_asserts"] = sum(1 for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++")
                           and re.search(r"\bassert\b|\bassert\.", l))
    m["wrote_test"] = m["test_added"] > 0 or m["src_asserts"] > 0
    return m


def run(task, check):
    passed, error = True, ""
    try:
        check()
    except Exception as e:  # AssertionError or a crash in the agent's code
        passed = False
        error = f"{type(e).__name__}: {e}"[:600] or traceback.format_exc()[-600:]
    try:
        metrics = _diff_metrics()
    except Exception as e:
        metrics = {"error": str(e)}
    out = os.environ.get("SC_METRICS")
    if out:
        with open(out, "a") as f:
            f.write(json.dumps({"task": task, "arm": os.environ.get("SC_ARM", "?"), "workdir": WORKDIR,
                                "passed": passed, "error": error, **metrics}) + "\n")
    if not passed:
        print(error, file=sys.stderr)
        sys.exit(1)
