# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

import os


def pytest_configure() -> None:
    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/woc")
    os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret")
