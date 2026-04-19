# Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
# Licensed under the Apache License, Version 2.0.

"""Wings of Capital - Shared Backend Module"""

__version__ = "1.0.0"
__author__ = "Bhargav (Wings of Capital)"
__license__ = "Apache License 2.0"

from .config import Settings, get_settings  # noqa: E402,F401
from .database import ENGINE, TIMESCALE_ENGINE, get_db, get_timescale_db  # noqa: E402,F401
from .logger import get_logger, init_logging, set_request_id  # noqa: E402,F401
from .redis import RedisClient, get_redis_client  # noqa: E402,F401
from .security import apply_cors, create_access_token, create_refresh_token, decode_token  # noqa: E402,F401
