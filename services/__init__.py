"""
E.A.D.A Shared Services
-----------------------
Provides access to the application's shared service container.
"""

from services.service_container import (
    ServiceContainer,
    services
)

__all__ = [
    "ServiceContainer",
    "services"
]