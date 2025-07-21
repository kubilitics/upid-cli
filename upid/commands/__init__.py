"""
UPID CLI Commands
"""

from . import auth
from . import cluster
from . import analyze
from . import optimize
from . import deploy
from . import report
from . import storage
from . import cloud

__all__ = ['auth', 'cluster', 'analyze', 'optimize', 'deploy', 'report', 'storage', 'cloud']
