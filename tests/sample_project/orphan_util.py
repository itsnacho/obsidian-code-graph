"""
Standalone abandoned utility file.
"""

import math


def calculate_entropy(values: list[float]) -> float:
    """Calculates Shannon entropy of a distribution."""
    total = sum(values)
    if total == 0:
        return 0.0
    probabilities = [v / total for v in values if v > 0]
    return -sum(p * math.log2(p) for p in probabilities)
