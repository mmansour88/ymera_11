
import os
def setup_tracing(app):
    if os.getenv("OTEL_ENABLED","1") != "1":
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from ..db import engine
        FastAPIInstrumentor().instrument_app(app)
        HTTPXClientInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument(engine=engine)
    except Exception:
        pass
