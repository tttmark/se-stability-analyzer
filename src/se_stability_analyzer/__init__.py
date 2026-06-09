"""Near-field and far-field shielding effectiveness stability analysis."""

from .analysis import AnalysisResult, FrequencyPoint, analyze_points, read_points

__all__ = [
    "AnalysisResult",
    "FrequencyPoint",
    "analyze_points",
    "read_points",
]

__version__ = "0.1.0"
