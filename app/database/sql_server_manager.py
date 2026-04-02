"""
SQL Server Manager - Investment Data Analysis Agent
==================================================

This module provides SQL Server management capabilities for the Investment Data Analysis Agent.
It serves as a compatibility layer for the DatabaseManager from connection.py.

Author: Investment Data Analysis Agent
"""

from .connection import DatabaseManager

# Export the main class for backward compatibility
__all__ = ['DatabaseManager']

# Create an alias for common usage patterns
SQLServerManager = DatabaseManager