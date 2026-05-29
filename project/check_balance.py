#!/usr/bin/env python3
"""Throwaway: print this OpenRouter API key's usage and remaining limit.

Hits /api/v1/key which returns key-specific usage and limit (not account-wide
totals). Reads OPENROUTER_API_KEY from ../.env or environment. Stdlib only.
Run: `python check_balance.py`
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip("'\""))

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    sys.exit("OPENROUTER_API_KEY not set")

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": f"Bearer {api_key}"},
)
with urllib.request.urlopen(req) as resp:
    data = json.load(resp).get("data", {})

usage = data.get("usage", 0)
limit = data.get("limit")

print("OpenRouter key status")
print(f"  Usage:     ${usage:.4f}")
if limit is None:
    print("  Limit:     none (account-wide credits apply)")
else:
    print(f"  Limit:     ${limit:.4f}")
    print(f"  Remaining: ${limit - usage:.4f}")
