import pytest
from backup.size_change_monitor import allowed_size_change, relative_size_change


def test_allowed_size_change_for_small_files():
    """ Returns large percentage for small files """
    assert allowed_size_change(1) > 10000
    assert allowed_size_change(100) > 2500


def test_allowed_size_change_for_large_files():
    """ Return small percentage for large files """
    assert allowed_size_change(1000000) < 100
    assert allowed_size_change(1000000000) < 10


def test_allowed_size_change_minimum_percentage():
    assert allowed_size_change(1000000000000) == 2


def test_relative_size_change():
    assert relative_size_change(2, 1) == 100
    assert relative_size_change(145, 100) == 45

    # Also support shrinkage
    assert relative_size_change(100, 145) == 31
