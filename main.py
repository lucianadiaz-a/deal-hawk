"""
Root-level entry point for Railway deployment.
This file allows Railway to auto-detect FastAPI and start the application.
"""
from backend.api.main import app

# Export the app for Railway/Railpack to detect
__all__ = ["app"]

