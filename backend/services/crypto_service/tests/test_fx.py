from unittest.mock import patch


def test_fetch_latest_rates():
    sample_payload = {"base": "EUR", "date": "2026-04-26", "rates": {"USD": 1.1, "GBP": 0.85}}

    class DummyResp:
        def raise_for_status(self):
            return None

        def json(self):
            return sample_payload

    with patch("crypto_service.market.frankfurter.requests.get", return_value=DummyResp()):
        from crypto_service.market.frankfurter import fetch_latest_rates

        res = fetch_latest_rates(base="EUR", symbols=["USD", "GBP"])  # type: ignore
        assert res["base"] == "EUR"
        assert "USD" in res["rates"]
