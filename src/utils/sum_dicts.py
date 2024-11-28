from typing import Dict


def sum_dicts(x: Dict, y: Dict) -> Dict:
    """Sums the values of two dicts where there are the same keys."""
    return {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}
