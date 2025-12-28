"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from backend.db import DbConfig

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str | bool]:
    """Health check endpoint."""
    try:
        cfg = DbConfig.from_env()
        return {
            "status": "ok",
            "db_path": str(cfg.path),
            "db_exists": cfg.path.exists(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


