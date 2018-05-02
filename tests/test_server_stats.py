
import pytest
import json
import unittest.mock as mock
from backup.s3_client import BackupStatus
from backup.server_stats import ServerStats, within_tolerance, format_backup_size


@pytest.fixture
def folder():
    return 'a/b/c'


@pytest.fixture
def dirs():
    return ['dir1', 'dir2']


def test_within_tolerance():
    assert within_tolerance(9, 10)
    assert within_tolerance(9.5, 10)
    assert within_tolerance(11, 10)
    assert not within_tolerance(8.99, 10)
    assert not within_tolerance(11.01, 10)


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
        "backup_status": "Missing previous backup",
        "last_backup_size": expected_size1,
        "previous_backup_size": 0
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size1
    mock_client.get_last_backup_folders.return_value = BackupStatus.NO_PREVIOUS_BACKUP, dirs
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == 0
    assert not stats.is_within_tolerance
    assert stats.json == expected_json


def test_server_json_generation_missing_current_backup(folder, dirs):
    expected_size2 = 2 ** 20
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": 'Missing current backup',
        "last_backup_size": 0,
        "previous_backup_size": expected_size2
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size2
    mock_client.get_last_backup_folders.return_value = BackupStatus.NO_CURRENT_BACKUP, dirs
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == 0
    assert stats.second_last_size == expected_size2
    assert not stats.is_within_tolerance
    assert stats.json == expected_json


def test_server_json_generation_outside_tolerance(folder, dirs):
    expected_size1, expected_size2 = 2 ** 20, 2 ** 30
    expected_json = json.dumps({
        "backup_folder": folder,
        "backup_status": f"Backup size is outside tolerance, now: {expected_size1}, previous: {expected_size2}",
        "last_backup_size": expected_size1,
        "previous_backup_size": expected_size2
    })
    mock_client = mock.Mock()
    mock_client.get_backup_size.side_effect = [expected_size1, expected_size2]
    mock_client.get_last_backup_folders.return_value = BackupStatus.OK, dirs
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size1
    assert stats.second_last_size == expected_size2
    assert not stats.is_within_tolerance
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
    mock_client.get_last_backup_folders.return_value = BackupStatus.OK, dirs
    stats = ServerStats(mock_client, folder)

    assert stats.last_size == expected_size
    assert stats.second_last_size == expected_size
    assert stats.is_within_tolerance
    assert stats.json == expected_json
