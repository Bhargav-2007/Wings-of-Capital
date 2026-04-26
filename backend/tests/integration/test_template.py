def test_service_root_health(test_client):
    """Simple smoke test that can be reused by service-level integration tests."""
    # Import here so the test runner resolves the package paths after conftest setup
    from auth_service.main import app as auth_app

    client = test_client(auth_app)
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "operational"
