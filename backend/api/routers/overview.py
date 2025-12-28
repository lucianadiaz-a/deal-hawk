"""Overview/dashboard endpoint."""
from __future__ import annotations

import sqlite3
from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from backend.api.dependencies import get_db_conn
from backend.api.schemas.overview import OverviewResponse
from backend.db import init_schema
from backend.services.dashboard import get_overview

router = APIRouter()


@router.get("/api/overview", response_model=OverviewResponse)
def get_overview_data(
    window_hours: int = Query(default=6, ge=1, le=168),
    threshold_pct: float = Query(default=10.0, ge=0.0, le=100.0),
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> OverviewResponse:
    """
    Get dashboard overview metrics, recent alerts, and near-miss listings.
    
    Args:
        window_hours: Time window for price deltas (1-168 hours)
        threshold_pct: Alert threshold percentage (0-100)
        conn: Database connection (injected)
        
    Returns:
        Overview data with metrics and feed items
    """
    init_schema(conn)
    
    metrics, recent_alerts, near_misses = get_overview(
        conn,
        window_hours=window_hours,
        threshold_pct=threshold_pct,
    )
    
    return OverviewResponse(
        metrics=asdict(metrics),
        recent_alerts=[asdict(item) for item in recent_alerts],
        near_misses=[asdict(item) for item in near_misses],
    )


