"""
User authentication service coordinating session management and security.
"""

from .crypto import hash_password, verify_password
import config
import database


class AuthService:
    """Core authentication logic for login and signup."""

    def __init__(self):
        self.db = database.Database()

    def register(self, username: str, password: str) -> bool:
        """Registers a new user and hashes password before storage."""
        hashed = hash_password(password)
        return self.db.save_user(username, hashed)

    def login(self, username: str, password: str) -> bool:
        """Validates credentials against database records."""
        stored_hash = self.db.get_user_password(username)
        if not stored_hash:
            return False
        return verify_password(password, stored_hash)
