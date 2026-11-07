"""
Cryptographic hashing and token verification utilities.
"""

import hashlib
import config


def hash_password(raw_password: str) -> str:
    """Hashes a password with SHA256 and the application secret key."""
    salted = f"{raw_password}:{config.SECRET_KEY}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, hashed: str) -> bool:
    """Compares raw password hash with stored hash."""
    return hash_password(raw_password) == hashed
