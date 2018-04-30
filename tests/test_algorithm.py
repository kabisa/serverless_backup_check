
from backup.algorithm import within_tolerance


def test_within_tolerance():
    assert within_tolerance(9, 10)
    assert within_tolerance(9.5, 10)
    assert within_tolerance(11, 10)
    assert not within_tolerance(8.99, 10)
    assert not within_tolerance(11.01, 10)
