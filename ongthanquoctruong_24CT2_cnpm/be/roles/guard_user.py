"""
Module: guard_user.py
Purpose: Defines the Guard User (Operator) role and privileges.
Guard Users operate the parking barriers, verify vehicles, and collect fees.
"""

def is_guard(user_session):
    """Check if the current user session belongs to a Guard (Operator)."""
    return user_session and user_session.get("role") in ["Operator", "Security"]

def get_guard_dashboard_url():
    return "/"
