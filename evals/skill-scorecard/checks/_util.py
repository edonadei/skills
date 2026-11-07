"""Shared helpers for this eval's checks. Each check runs in the attempt workdir."""
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

EVAL = Path("scorecard")
CANDIDATE = Path(os.environ["SC_CANDIDATE"])


def load(path):
    p = EVAL / path
    assert p.exists(), f"{p} is missing"
    return json.loads(p.read_text())


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", head[16:24])


def slides_ok():
    """Re-render the slides from the agent's copy.json and require every slide inside its margins."""
    summary = sorted(EVAL.glob("summary-*.json"), key=lambda p: len(p.name))
    assert summary, "no summary-*.json: aggregate.py was never run"
    r = subprocess.run([sys.executable, "report/render_slides.py", summary[-1].name], cwd=EVAL,
                       capture_output=True, text=True, timeout=28)
    assert r.returncode == 0, f"render_slides failed: {(r.stderr or r.stdout)[-300:]}"
    bad = [l for l in r.stdout.splitlines() if l.startswith("slide") and not l.endswith("ok")]
    assert not bad, f"slides cross their margins: {bad}"
    for i in range(1, 5):
        assert png_size(EVAL / f"report/slides/slide-{i}.png") == (2160, 1800), f"slide-{i}.png is not 2160x1800"


def text_of(obj):
    return json.dumps(obj, ensure_ascii=False)


def percents(s):
    return {int(m) for m in re.findall(r"(\d+)(?:\.\d+)?\s?%", s)}
