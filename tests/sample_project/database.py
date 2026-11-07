"""
Database connection pool and query execution layer.
"""

import config
# Circular import for testing cycle detection
from auth.service import AuthService


class Database:
    """Mock database storage."""

    def __init__(self):
        self.url = config.Config().get_db_url()
        self.users = {}

    def save_user(self, username: str, password_hash: str) -> bool:
        """Saves a user record to mock database."""
        self.users[username] = password_hash
        return True

    def get_user_password(self, username: str) -> str | None:
        """Retrieves stored hash for user."""
        return self.users.get(username)
