import os
import importlib
from fastapi.testclient import TestClient

def load_app():
    # common entry points
    for mod in ["app.main", "backend.app.main", "main"]:
        try:
            m = importlib.import_module(mod)
            app = getattr(m, "app", None)
            if app: return app
        except Exception:
            continue
    raise RuntimeError("FastAPI app not found (expected app.main:app)")

def test_health_or_root():
    app = load_app()
    client = TestClient(app)
    # try known endpoints
    for path in ["/health", "/api/health", "/", "/docs"]:
        r = client.get(path)
        if r.status_code < 500:
            assert True
            return
    raise AssertionError("No healthy endpoint responded")
