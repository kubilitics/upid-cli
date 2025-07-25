"""
UPID CLI API Server - Database Base
Shared database base classes and metadata
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Shared metadata for all tables
metadata = MetaData()

# Shared Base class for all models
Base = declarative_base(metadata=metadata)