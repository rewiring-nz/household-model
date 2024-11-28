from utils.sum_dicts import sum_dicts


def test_sum_dicts():
    x = {"a": 1, "b": 2}
    y = {"b": 10, "c": 100}
    expected = {"a": 1, "b": 12, "c": 100}
    result = sum_dicts(x, y)
    assert result == expected
