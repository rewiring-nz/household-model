from typing import Dict, List


def sum_dicts(dicts: List[Dict]) -> Dict:
    """Sums the values of multiple dicts where there are the same keys."""
    all_keys = set().union(*dicts)
    return {k: sum(d.get(k, 0) for d in dicts) for k in all_keys}
