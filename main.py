
import os
from fastapi import FastAPI
from .startup import boot_checks
from fastapi.middleware.cors import CORSMiddleware
from .middleware.rate_limit import RateLimiterMiddleware
from .middleware.otel import setup_tracing
from .routers import storage, agents, reports, webhooks, evals, routing, memory, rooms, admin, skills
from .auth.rbac import auth_router

def create_app() -> FastAPI:
    app = FastAPI(title="YMERA Fullstack — Phases 1–24 (v1)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ALLOW_ORIGINS","*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_tracing(app)
    if os.getenv("RATE_LIMIT_ENABLED","1") == "1":
        app.add_middleware(RateLimiterMiddleware)

    # Routers
    app.include_router(auth_router, prefix="/v1/auth", tags=["auth"])
    app.include_router(storage.router, prefix="/v1/storage", tags=["storage"])
    app.include_router(agents.router, prefix="/v1/agents", tags=["agents"])
    app.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
    app.include_router(webhooks.router, prefix="/v1/webhooks", tags=["webhooks"])
    app.include_router(evals.router, prefix="/v1/evals", tags=["evals"])
    app.include_router(admin.router, prefix="/v1/admin", tags=["admin"])
    app.include_router(skills.router, prefix="/v1/skills", tags=["skills"])\n    app.include_router(memory.router, prefix="/v1/memory", tags=["memory"])\n    app.include_router(rooms.router, prefix="/v1/rooms", tags=["rooms"])
    app.include_router(routing.router, prefix="/v1/routing", tags=["routing"])

    @app.get("/healthz")
    def health():
        return {"ok": True}

    return app

app = create_app()
