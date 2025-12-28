"""FastAPI application entrypoint for Deal Hawk API."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import health, listings, overview, products

# Create FastAPI app
app = FastAPI(
    title="Deal Hawk API",
    description="Price monitoring and alert API",
    version="0.1.0",
)

# Configure CORS for local development with Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


