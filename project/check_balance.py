#!/usr/bin/env python3
"""Throwaway: print this OpenRouter API key's usage and remaining limit.

Hits /api/v1/key which returns key-specific usage and limit (not account-wide
totals). Reads OPENROUTER_API_KEY from ../.env or environment.
Run: `python check_balance.py`
"""

import os
import sys
from pathlib import Path

import httpx

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    sys.exit("OPENROUTER_API_KEY not set")

resp = httpx.get(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": f"Bearer {api_key}"},
)
resp.raise_for_status()
data = resp.json().get("data", {})

usage = data.get("usage", 0)
limit = data.get("limit")

print("OpenRouter key status")
print(f"  Usage:     ${usage:.4f}")
if limit is None:
    print("  Limit:     none (account-wide credits apply)")
else:
    print(f"  Limit:     ${limit:.4f}")
    print(f"  Remaining: ${limit - usage:.4f}")
