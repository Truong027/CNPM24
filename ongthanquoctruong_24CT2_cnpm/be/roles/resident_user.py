"""
Module: resident_user.py
Purpose: Defines the Resident User role and privileges.
Resident Users can view their parking history, register vehicles, and manage their profile.
"""

def is_resident(user_session):
    """Check if the current user session belongs to a Resident."""
    return user_session and user_session.get("role") == "Resident"

def get_resident_dashboard_url():
    return "/resident-dashboard"
