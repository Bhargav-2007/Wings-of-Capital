import pytest


def test_password_strength_validator_accepts_strong():
    from auth_service.utils.passwords import validate_password_strength

    # A password that meets the default rules (uppercase, lowercase, number, symbol)
    validate_password_strength("StrongPassw0rd!")


def test_rate_limiter_enforcement():
    from shared.security import RateLimiter
    from shared.exceptions import RateLimitError

    rl = RateLimiter()
    key = "tests:rate:1"

    # Allow two increments then block on the third when limit=2
    rl.enforce(key, limit=2)
    rl.enforce(key, limit=2)
    with pytest.raises(RateLimitError):
        rl.enforce(key, limit=2)
