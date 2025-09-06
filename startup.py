import os, logging
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import engine, SessionLocal
from alembic import command
from alembic.config import Config
import redis

log = logging.getLogger("ymera.startup")

@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _alembic_cfg():
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "..", "alembic"))
    return cfg

def run_migrations():
    try:
        command.upgrade(_alembic_cfg(), "head")
        log.info("Alembic migrations applied ✅")
    except Exception as e:
        log.error("Alembic migration failed: %s", e)

def check_pgvector():
    with engine.connect() as con:
        try:
            con.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            con.commit()
            log.info("pgvector available/enabled ✅")
        except SQLAlchemyError as e:
            log.warning("pgvector not available: %s", e)

def check_redis():
    url = os.getenv("REDIS_URL", "")
    if not url:
        log.warning("REDIS_URL not set; realtime features may be limited")
        return
    try:
        r = redis.from_url(url)
        r.ping()
        log.info("Redis reachable ✅")
    except Exception as e:
        log.warning("Redis NOT reachable: %s", e)

def boot_checks():
    log.info("Running startup checks...")
    check_pgvector()
    run_migrations()
    check_redis()
    log.info("Startup checks complete.")
