"""
Main application entry point.
"""

from auth.service import AuthService
import config


def bootstrap():
    """Initializes settings and runs the main loop."""
    print(f"Starting app in {config.ENV} mode...")
    auth = AuthService()
    return auth


if __name__ == "__main__":
    bootstrap()
