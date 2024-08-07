import pandas as pd

NUM_TO_INT_MAP_HEATERS = {
    'Five or more': 5,
    'Four': 4,
    'Three': 3,
    'Two': 2,
    'One': 1,
}
NUM_TO_INT_MAP_VEHICLES = {
    'More than five': 6,
    'Five': 5,
    'Four': 4,
    'Three': 3,
    'Two': 2,
    'One': 1,
    'None': 0,
}


def cast_num_to_int(x, mapping=NUM_TO_INT_MAP_HEATERS) -> int:
    if pd.isna(x):
        return 0
    return mapping[x]
