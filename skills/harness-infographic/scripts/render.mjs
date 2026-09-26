#!/usr/bin/env node
// Render an HTML card to PNG with headless Chrome/Edge via the DevTools protocol.
// No npm dependencies (needs Node >= 22 for the global WebSocket).
// Usage: node render.mjs <in.html> <out.png> [width=1080] [height=1350] [scale=2]
//
// Why CDP instead of `chrome --screenshot`: in new headless mode --window-size
// includes browser chrome, so the viewport comes out ~95px short and the bottom
// of the card (the footer) gets clipped. Emulation.setDeviceMetricsOverride
// sets the exact viewport.
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
import { tmpdir } from "node:os";

const [, , input, output, w = "1080", h = "1350", scale = "2"] = process.argv;
if (!input || !output) {
  console.error("usage: node render.mjs <in.html> <out.png> [width] [height] [scale]");
  process.exit(2);
}
const width = Number(w), height = Number(h), deviceScaleFactor = Number(scale);

const chrome = [
  process.env.CHROME_PATH,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].filter(Boolean).find((p) => existsSync(p));
if (!chrome) {
  console.error("No Chrome/Edge found; set CHROME_PATH.");
  process.exit(1);
}

// A throwaway profile keeps headless Chrome from colliding with a running browser.
const profile = mkdtempSync(join(tmpdir(), "card-render-"));
const proc = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
  "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank",
]);

function cleanup() {
  proc.kill();
  // Chrome may hold the profile briefly after exit; best effort.
  setTimeout(() => rmSync(profile, { recursive: true, force: true }), 500);
}

try {
  const browserWs = await new Promise((ok, fail) => {
    const t = setTimeout(() => fail(new Error("Chrome did not start")), 15000);
    let buf = "";
    proc.stderr.on("data", (d) => {
      buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearTimeout(t); ok(m[1]); }
    });
  });
  const port = new URL(browserWs).port;
  const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = pages.find((p) => p.type === "page");

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok) => ws.addEventListener("open", ok, { once: true }));
  let id = 0;
  const pending = new Map();
  const events = new Map();
  ws.addEventListener("message", (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) {
      const { ok, fail } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? fail(new Error(msg.error.message)) : ok(msg.result);
    } else if (msg.method && events.has(msg.method)) {
      events.get(msg.method)();
      events.delete(msg.method);
    }
  });
  const send = (method, params = {}) => new Promise((ok, fail) => {
    pending.set(++id, { ok, fail });
    ws.send(JSON.stringify({ id, method, params }));
  });
  const once = (method) => new Promise((ok) => events.set(method, ok));

  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor, mobile: false });
  const loaded = once("Page.loadEventFired");
  await send("Page.navigate", { url: pathToFileURL(resolve(input)).href });
  await loaded;
  await send("Runtime.evaluate", { expression: "document.fonts.ready.then(() => true)", awaitPromise: true });

  // Warn when content spills past the card — that text would be cut from the image.
  const { result } = await send("Runtime.evaluate", {
    expression: `[...document.querySelectorAll('.card *')].filter(e => {
      const r = e.getBoundingClientRect();
      return r.width && (r.bottom > ${height} + 0.5 || r.right > ${width} + 0.5 || e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflow === 'hidden');
    }).map(e => e.tagName.toLowerCase() + (e.className ? '.' + e.className : '')).slice(0, 5)`,
    returnByValue: true,
  });

  const shot = await send("Page.captureScreenshot", {
    format: "png",
    clip: { x: 0, y: 0, width, height, scale: 1 },
  });
  writeFileSync(resolve(output), Buffer.from(shot.data, "base64"));
  ws.close();
  console.log(`rendered ${resolve(output)} (${width}x${height} @${deviceScaleFactor}x)`);
  if (result.value?.length) console.warn(`WARNING overflow: ${result.value.join(", ")} extends past the card — shorten the text`);
} finally {
  cleanup();
}
