"""
Configuration management and environment variable loader.
"""

import os
import sys

ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")


class Config:
    """Application configuration holder."""

    def __init__(self, debug: bool = True):
        self.debug = debug

    def get_db_url(self) -> str:
        """Constructs the database connection string."""
        return os.getenv("DATABASE_URL", "sqlite:///app.db")
