"""Render the 4 X images (from the eval dir):
    python3 report/render_slides.py summary-<tags>.json  ->  report/slides/slide-{1..4}.png
1440x1200 CSS px (6:5, the shape X's multi-image carousel shows uncropped) at 1.5x.
Prints, per slide, any element crossing the 88px side margin or the slide's bottom: fix
those before posting.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
summary = json.loads(Path(sys.argv[1]).read_text())
copy = json.loads((HERE / "copy.json").read_text())
meta = json.loads(Path("meta.json").read_text())
data = json.dumps({"arms": summary["arms"], "runs": summary["runs"], "activation": summary["activation"],
                   "tasks": meta["tasks"], "claims": copy["claims"], "s": copy["slides"]}).replace("</", "<\\/")
page = HERE / ".slides.render.html"
page.write_text((HERE / "slides.html").read_text().replace("__DATA__", data))
out = HERE / "slides"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1600, "height": 1300}, device_scale_factor=1.5)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(page.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(500)
    if errors:
        sys.exit(f"slide script error: {errors[0]}")
    for i in range(1, 5):
        el = pg.locator(f"#s{i}")
        over = el.evaluate("""s => { const q = s.getBoundingClientRect();
            return [...s.querySelectorAll('*')].filter(e => { const r = e.getBoundingClientRect();
              return r.width && (r.right > q.right - 87 || r.left < q.left + 87 || r.bottom > q.bottom + 0.5); })
            .map(e => (e.className || e.tagName) + ':' + (e.textContent || '').trim().slice(0, 30)); }""")
        el.screenshot(path=str(out / f"slide-{i}.png"))
        print(f"slide {i}: {'ok' if not over else 'OUTSIDE MARGIN: ' + '; '.join(over[:4])}")
    b.close()
page.unlink()
