"""
FastAPI entrypoint required by task specification.
This module delegates to src.api to keep logic clean.
"""

from src.api import app

__all__ = ["app"]
