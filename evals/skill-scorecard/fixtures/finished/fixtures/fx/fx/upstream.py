"""Treasury FX API client. Slow (~800ms) and rate-limited to 60 req/min."""
import json
import time
import urllib.request
from decimal import Decimal

BASE_URL = "https://fx.treasury.internal/v2/rates"


def get_rate(base: str, quote: str) -> Decimal:
    with urllib.request.urlopen(f"{BASE_URL}?base={base}&quote={quote}", timeout=5) as resp:
        return Decimal(str(json.load(resp)["rate"]))
