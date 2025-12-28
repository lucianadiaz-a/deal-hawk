"""FastAPI application entrypoint for Deal Hawk API."""
from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import health, listings, overview, products
from backend.db import DbConfig, db_conn, init_schema

# Initialize database schema on startup if needed
def _ensure_db_initialized() -> None:
    """Ensure database schema is initialized."""
    try:
        cfg = DbConfig.from_env()
        with db_conn(cfg) as conn:
            # Check if schema exists by checking for products table
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
            )
            if cursor.fetchone() is None:
                # Schema doesn't exist, initialize it
                init_schema(conn)
                print(f"✓ Database schema initialized at {cfg.path}")
            else:
                print(f"✓ Database schema already exists at {cfg.path}")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize database: {e}")
        # Don't fail startup if DB init fails - let the app try to connect later

# Create FastAPI app
app = FastAPI(
    title="Deal Hawk API",
    description="Price monitoring and alert API",
    version="0.1.0",
)

# Configure CORS - allow localhost for dev and production frontend URL
frontend_url = os.getenv("FRONTEND_URL", "")
cors_origins = [
    "http://localhost:5173",  # Vite dev server default
    "http://127.0.0.1:5173",
    "https://deal-hawk-frontend-production.up.railway.app",  # Production frontend
]
if frontend_url:
    cors_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
_ensure_db_initialized()

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(overview.router, tags=["overview"])
app.include_router(products.router, tags=["products"])
app.include_router(listings.router, tags=["listings"])


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "Deal Hawk API",
        "version": "0.1.0",
        "docs": "/docs",
    }


