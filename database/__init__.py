"""
E.A.D.A Database Module
-----------------------
Provides persistent storage and higher-level services
for AI task-decision history.
"""

from database.database_service import DatabaseService
from database.models import Database

__all__ = [
    "Database",
    "DatabaseService"
]