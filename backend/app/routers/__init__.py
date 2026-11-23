"""
Routers Package.
"""

from .auth import router as auth_router
from .api_keys import router as api_keys_router
from .papers import router as papers_router
from .questions import router as questions_router
from .analysis import router as analysis_router
from .predictions import router as predictions_router
from .mock_exams import router as mock_exams_router
