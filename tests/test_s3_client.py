import unittest.mock as mock

import pytest

from backup import s3_utils
from backup.s3_utils import get_backup_size


def get_mock_s3_obj(key, size):
    s3_obj = mock.Mock()
    s3_obj.key = key
    s3_obj.size = size
    return s3_obj


@pytest.fixture
def prefix_short():
    return 'a/b/c'


def test_get_backup_size(prefix_short):
    s3_utils.iterate_objects = mock.Mock()
    s3_utils.iterate_objects.return_value = [get_mock_s3_obj('key1', 200), get_mock_s3_obj('key2', 300)]
    assert get_backup_size('my-first-bucket', prefix_short) == 500
