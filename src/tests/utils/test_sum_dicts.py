from utils.sum_dicts import sum_dicts


def test_sum_dicts():
    x = {"a": 1, "b": 2}
    y = {"b": 10, "c": 100}
    expected = {"a": 1, "b": 12, "c": 100}
    result = sum_dicts([x, y])
    assert result == expected

    dicts = [{"a": 1, "b": 2}, {"b": 3, "c": 4}, {"a": 5, "d": 6}]
    result = sum_dicts(dicts)
    assert result == {"a": 6, "b": 5, "c": 4, "d": 6}
