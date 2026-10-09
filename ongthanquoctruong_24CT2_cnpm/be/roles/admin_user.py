"""
Module: admin_user.py
Purpose: Defines the Admin User role and privileges.
Admin Users are responsible for managing the system, creating other users, and viewing overall statistics.
"""

def is_admin(user_session):
    """Check if the current user session belongs to an Admin."""
    return user_session and user_session.get("role") == "Admin"

def get_admin_dashboard_url():
    return "/"
