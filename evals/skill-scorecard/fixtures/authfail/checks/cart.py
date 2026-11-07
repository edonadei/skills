import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import json

JS = r"""
import { total } from './src/cart.js';
const cart = { items: [{ sku: 'MUG', unitCents: 1250, qty: 2 }, { sku: 'TEE', unitCents: 1999, qty: 1 }] };
const small = { items: [{ sku: 'PIN', unitCents: 300, qty: 1 }] };
const out = {};
const run = (k, f) => { try { out[k] = { ok: f() }; } catch (e) { out[k] = { err: String(e && e.message || e) }; } };
run('plain', () => total(cart));
run('pct', () => total(cart, 'WELCOME10'));
run('fixed', () => total(cart, 'FIVEOFF'));
run('floor', () => total(small, 'FIVEOFF'));
run('expired', () => total(cart, 'BLACKFRIDAY'));
run('unknown', () => total(cart, 'NOPE'));
run('none', () => total(cart, undefined));
console.log(JSON.stringify(out));
"""


def check():
    r = sh("node", "--input-type=module", "-e", JS)
    assert r.returncode == 0, f"node crashed: {r.stderr[-400:]}"
    res = json.loads(r.stdout.strip().splitlines()[-1])
    assert res["plain"].get("ok") == 5399, f"total(cart) changed: {res['plain']}"
    assert res["none"].get("ok") == 5399, f"total(cart, undefined) broken: {res['none']}"
    assert res["pct"].get("ok") == 4859, f"WELCOME10 (10% off before VAT) should be 4859, got {res['pct']}"
    assert res["fixed"].get("ok") == 4799, f"FIVEOFF (500c off before VAT) should be 4799, got {res['fixed']}"
    assert res["floor"].get("ok") == 0, f"fixed discount larger than the cart must floor at 0, got {res['floor']}"
    assert "err" in res["expired"], f"expired BLACKFRIDAY was accepted: {res['expired']}"
    assert "err" in res["unknown"], f"unknown code was accepted: {res['unknown']}"
    node_test_ok()


run("cart", check)
