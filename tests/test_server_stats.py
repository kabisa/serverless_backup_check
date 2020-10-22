import os

import pytest
import datetime
import json
import unittest.mock as mock

from backup import s3_utils
import backup.server_stats
from backup.server_stats import ServerStats
from backup.server_stats import (
    format_backup_size,
    get_backup_prefix_keys,
    date_to_prefix,
)


@pytest.fixture
def folder():
    return "a/b/c"


@pytest.fixture
def dirs():
    return ["dir1", "dir2"]


@pytest.fixture
def prefix_long():
    return "1/2/3/4/5/6/7/8/9"


@pytest.fixture
def bucket_name():
    return "my_test_bucket"


@pytest.fixture
def good_key():
    return "good_key"


def get_mock_s3_obj(key, size=0):
    s3_obj = mock.Mock()
    s3_obj.key = key
    s3_obj.size = size
    return s3_obj


@pytest.fixture
def mock_obj_iterator(good_key):
    s3_utils.iterate_objects = mock.Mock()
    s3_utils.iterate_objects.return_value = [get_mock_s3_obj(good_key)]
    return s3_utils.iterate_objects


def test_date_to_prefix(prefix_long):
    jan82017 = datetime.datetime(year=2017, month=1, day=8)
    may12018 = datetime.datetime(year=2018, month=5, day=1)
    sept182020 = datetime.datetime(year=2020, month=9, day=18)
    assert date_to_prefix(prefix_long, jan82017, None) == os.path.join(
        prefix_long, "2017.01.08"
    )
    assert date_to_prefix(prefix_long, may12018, None) == os.path.join(
        prefix_long, "2018.05.01"
    )
    assert date_to_prefix(prefix_long, sept182020, None) == os.path.join(
        prefix_long, "2020.09.18"
    )
    assert date_to_prefix(prefix_long, sept182020, "%Y-%m-%d") == os.path.join(
        prefix_long, "2020-09-18"
    )
    assert date_to_prefix("", sept182020, "a/b/c/%Y-%m-%d") == "a/b/c/2020-09-18"
    with pytest.raises(ValueError):
        assert date_to_prefix(None, sept182020, "a/b/c/%Y-%m-%d") == "a/b/c/2020-09-18"


def test_get_backup_prefix_keys(bucket_name, prefix_long, mock_obj_iterator):
    today = datetime.datetime.today()
    one_day_ago = today - datetime.timedelta(days=1)
    two_days_ago = today - datetime.timedelta(days=2)
    key1, key2 = one_day_ago, two_days_ago
    full_path1, full_path2 = (
        date_to_prefix(prefix_long, key1, None),
        date_to_prefix(prefix_long, key2, None),
    )
    mock_obj_iterator.return_value = [full_path1, full_path2]
    assert get_backup_prefix_keys(prefix_long, None) == (full_path1, full_path2)


def test_format_backup_size():
    assert format_backup_size(0) == "0 Bytes"
    assert format_backup_size(1) == "1 Byte"
    assert format_backup_size(1023) == "1023 Bytes"
    assert format_backup_size(2 ** 10) == "1.0 KiB"
    assert format_backup_size((2 ** 10) * 1.1) == "1.1 KiB"
    assert format_backup_size((2 ** 20) - (2 ** 10)) == "1023.0 KiB"
    assert format_backup_size(2 ** 20) == "1.0 MiB"
    assert format_backup_size((2 ** 20) * 1.1) == "1.1 MiB"
    assert format_backup_size((2 ** 30) - (2 ** 20)) == "1023.0 MiB"
    assert format_backup_size(2 ** 30) == "1.0 GiB"
    assert format_backup_size((2 ** 30) * 1.1) == "1.1 GiB"


def test_server_json_generation_missing_previous_backup(folder, dirs):
    expected_size1 = 2 ** 30
    one_day_ago = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.date.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    expected_json = json.dumps(
        {
            "backup_folder": folder,
            "backup_status": f"Missing backup from {two_days_ago}",
            "last_backup_size": format_backup_size(expected_size1),
            "previous_backup_size": format_backup_size(0),
            "last_backup_date": one_day_ago,
            "previous_backup_date": two_days_ago,
        },
        sort_keys=True,
    )
    backup.server_stats.get_backup_size = mock.Mock()
    backup.server_stats.get_backup_size.side_effect = [expected_size1, 0]
    stats = ServerStats('some-bucket', folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == 0
    assert stats.json == expected_json


def test_server_json_generation_missing_current_backup(folder, dirs):
    expected_size2 = 2 ** 20
    one_day_ago = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.date.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    expected_json = json.dumps(
        {
            "backup_folder": folder,
            "backup_status": f"Missing backup from {one_day_ago}",
            "last_backup_size": format_backup_size(0),
            "previous_backup_size": format_backup_size(expected_size2),
            "last_backup_date": one_day_ago,
            "previous_backup_date": two_days_ago,
        },
        sort_keys=True,
    )
    backup.server_stats.get_backup_size = mock.Mock()
    backup.server_stats.get_backup_size.side_effect = [0, expected_size2]
    stats = ServerStats('some-bucket', folder)

    assert stats.last_size == 0
    assert stats.second_last_size == expected_size2
    assert stats.json == expected_json


def test_server_json_generation_outside_tolerance(folder, dirs):
    expected_size1, expected_size2 = 2 ** 20, 2 ** 30
    one_day_ago = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.date.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    expected_json = json.dumps(
        {
            "backup_folder": folder,
            "backup_status": f"Backup size is outside tolerance",
            "last_backup_size": format_backup_size(expected_size1),
            "previous_backup_size": format_backup_size(expected_size2),
            "last_backup_date": one_day_ago,
            "previous_backup_date": two_days_ago,
        },
        sort_keys=True,
    )
    backup.server_stats.get_backup_size.side_effect = [expected_size1, expected_size2]
    stats = ServerStats('some-bucket', folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == expected_size2
    assert stats.json == expected_json


def test_server_json_generation_happy_path(folder, dirs):
    expected_size = 2 ** 20  # 1 MB
    one_day_ago = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.date.today() - datetime.timedelta(2)).strftime("%Y-%m-%d")
    expected_json = json.dumps(
        {
            "backup_folder": folder,
            "backup_status": "Backup OK",
            "last_backup_size": format_backup_size(expected_size),
            "previous_backup_size": format_backup_size(expected_size),
            "last_backup_date": one_day_ago,
            "previous_backup_date": two_days_ago,
        },
        sort_keys=True,
    )
    backup.server_stats.get_backup_size = mock.Mock()
    backup.server_stats.get_backup_size.return_value = expected_size
    stats = ServerStats('some-bucket', folder)

    assert stats.last_size == expected_size
    assert stats.second_last_size == expected_size
    assert stats.json == expected_json
