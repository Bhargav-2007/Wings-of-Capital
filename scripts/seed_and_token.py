#!/usr/bin/env python3
# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Seed crypto data and generate a matching dev token."""

from __future__ import annotations

import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed crypto data and generate a dev token")
    parser.add_argument("--symbols", default="BTC,ETH,SOL,USDT", help="Comma-separated symbols")
    parser.add_argument("--days", type=int, default=30, help="Days of price history")
    args = parser.parse_args()

    seed_cmd = [
        sys.executable,
        "scripts/seed_crypto_data.py",
        "--days",
        str(args.days),
        "--symbols",
        args.symbols,
    ]

    result = subprocess.run(seed_cmd, check=True, capture_output=True, text=True)
    print(result.stdout.strip())

    user_id = None
    for line in result.stdout.splitlines():
        if "'user_id':" in line:
            user_id = line.split("'user_id':", 1)[1].split("'")[1]
            break

    if not user_id:
        raise RuntimeError("Unable to parse user_id from seed output")

    token_cmd = [
        sys.executable,
        "scripts/dev_token.py",
        "--user-id",
        user_id,
    ]

    token_result = subprocess.run(token_cmd, check=True, capture_output=True, text=True)
    print(token_result.stdout.strip())


if __name__ == "__main__":
    main()
