# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

from shared.logger import init_logging


def test_logger_initialization():
    init_logging("test-service", "INFO", use_json=True)
