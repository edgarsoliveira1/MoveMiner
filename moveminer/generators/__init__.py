"""
This module contains different statistical models to
generate trajectories given certain statistical constrains.

All the resources of this module should be imported directly
from ``yupi.generators``.
"""

from moveminer.generators.generators import (
    Generator,
    RandomWalkGenerator,
)

__all__ = ["Generator", "RandomWalkGenerator"]