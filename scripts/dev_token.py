#!/usr/bin/env python3
# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Generate a development JWT access token."""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "backend" / "services"
sys.path.insert(0, str(SERVICES_DIR))

os.environ.setdefault("DATABASE_URL", "postgresql://woc_user:woc_password@localhost:5432/wings_of_capital")
os.environ.setdefault("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

from shared.security import create_access_token  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a dev access token")
    parser.add_argument("--user-id", default=None, help="User id to embed in token")
    args = parser.parse_args()

    user_id = args.user_id or str(uuid.uuid4())
    token = create_access_token(user_id)

    print("USER_ID=", user_id)
    print("TOKEN=", token)


if __name__ == "__main__":
    main()
