import pandas as pd


def get_test_data(csv_path: str) -> dict:
    return (
        pd.read_csv(csv_path, index_col='col')
        .T.loc['val']
        .replace({'0': 0, '1': 1})
        .to_dict()
    )
