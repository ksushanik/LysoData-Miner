"""
API modules initialization
=========================
Import and configure all API routers.
"""

from .health import router as health_router
from .strains import router as strains_router
from .tests import router as tests_router
from .identification import router as identification_router

__all__ = [
    "health_router",
    "strains_router", 
    "tests_router",
    "identification_router"
] 