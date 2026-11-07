"""Render the report page (from the eval dir):
    python3 report/build.py summary-<tags>.json  ->  report/scorecard.html
Task rows come from meta.json (in its order); every word on the page comes from report/copy.json.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
summary = json.loads(Path(sys.argv[1]).read_text())
meta = json.loads(Path("meta.json").read_text())
copy = json.loads((HERE / "copy.json").read_text())
present = set().union(*(a["tasks"].keys() for a in summary["arms"].values()))
data = {
    "arms": summary["arms"],
    "tasks": [{"key": k, "label": t["label"], "what": t["what"], "cat": t["kind"]}
              for k, t in meta["tasks"].items() if k in present],
    **copy,
}
html = (HERE / "template.html").read_text().replace("__TITLE__", copy["title"])
out = HERE / "scorecard.html"
out.write_text(html.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(out)
