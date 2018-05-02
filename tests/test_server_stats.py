
import pytest
import datetime
import json
import unittest.mock as mock
import backup.s3_client as s3_client
from backup.server_stats import ServerStats, within_tolerance
from backup.server_stats import format_backup_size, get_backup_prefix_keys, date_to_prefix


@pytest.fixture
def folder():
    return 'a/b/c'


@pytest.fixture
def dirs():
    return ['dir1', 'dir2']


@pytest.fixture
def prefix_long():
    return '1/2/3/4/5/6/7/8/9'


@pytest.fixture
def bucket_name():
    return 'my_test_bucket'


@pytest.fixture
def good_key():
    return 'good_key'


@pytest.fixture
def mock_obj_key_iterator(good_key):
    s3_client.obj_key_iterator = mock.Mock()
    s3_client.obj_key_iterator.return_value = [good_key]
    return s3_client.obj_key_iterator


def test_within_tolerance():
    assert within_tolerance(9, 10)
    assert within_tolerance(9.5, 10)
    assert within_tolerance(11, 10)
    assert not within_tolerance(8.99, 10)
    assert not within_tolerance(11.01, 10)


def test_date_to_prefix(prefix_long):
    jan82017 = datetime.datetime(year=2017, month=1, day=8)
    may12018 = datetime.datetime(year=2018, month=5, day=1)
    sept182020 = datetime.datetime(year=2020, month=9, day=18)
    assert date_to_prefix(prefix_long, jan82017) == '/'.join([prefix_long, '2017.01.08'])
    assert date_to_prefix(prefix_long, may12018) == '/'.join([prefix_long, '2018.05.01'])
    assert date_to_prefix(prefix_long, sept182020) == '/'.join([prefix_long, '2020.09.18'])


def test_get_backup_prefix_keys(bucket_name, prefix_long, mock_obj_key_iterator):
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    key1, key2 = today, yesterday
    full_path1, full_path2 = date_to_prefix(prefix_long, key1), date_to_prefix(prefix_long, key2)
    mock_obj_key_iterator.return_value = [full_path1, full_path2]
    assert get_backup_prefix_keys(prefix_long) == (full_path1, full_path2)


def test_format_backup_size():
    assert format_backup_size(0) == '0 Bytes'
    assert format_backup_size(1) == '1 Byte'
    assert format_backup_size(1023) == '1023 Bytes'
    assert format_backup_size(2 ** 10) == '1.0 KiB'
    assert format_backup_size((2 ** 10) * 1.1) == '1.1 KiB'
    assert format_backup_size((2 ** 20) - (2 ** 10)) == '1023.0 KiB'
    assert format_backup_size(2 ** 20) == '1.0 MiB'
    assert format_backup_size((2 ** 20) * 1.1) == '1.1 MiB'
    assert format_backup_size((2 ** 30) - (2 ** 20)) == '1023.0 MiB'
    assert format_backup_size(2 ** 30) == '1.0 GiB'
    assert format_backup_size((2 ** 30) * 1.1) == '1.1 GiB'


def test_server_json_generation_missing_previous_backup(folder, dirs):
    expected_size1 = 2 ** 30
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": "Missing previous backup.",
        "last_backup_size": expected_size1,
        "previous_backup_size": 0
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.side_effect = [expected_size1, 0]
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == 0
    assert stats.json == expected_json


def test_server_json_generation_missing_current_backup(folder, dirs):
    expected_size2 = 2 ** 20
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": 'Missing current backup.',
        "last_backup_size": 0,
        "previous_backup_size": expected_size2
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.side_effect = [0, expected_size2]
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == 0
    assert stats.second_last_size == expected_size2
    assert stats.json == expected_json


def test_server_json_generation_outside_tolerance(folder, dirs):
    expected_size1, expected_size2 = 2 ** 20, 2 ** 30
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": f"Backup size is outside tolerance, now: {expected_size1}, previous: {expected_size2}.",
        "last_backup_size": expected_size1,
        "previous_backup_size": expected_size2
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.side_effect = [expected_size1, expected_size2]
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == expected_size2
    assert stats.json == expected_json


def test_server_json_generation_happy_path(folder, dirs):
    expected_size = 2 ** 20  # 1 MB
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": "Backup OK.",
        "last_backup_size": expected_size,
        "previous_backup_size": expected_size
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size
    assert stats.second_last_size == expected_size
    assert stats.json == expected_json
