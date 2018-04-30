
import unittest.mock as mock
from backup.s3_client import BackupStatus
from backup.server_stats import ServerStats, within_tolerance, format_backup_size


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


def test_server_report_generation_missing_previous_backup():
    expected_size1 = 2 ** 30
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size1
    mock_client.get_last_backup_folders.return_value = BackupStatus.NO_PREVIOUS_BACKUP, ['dir1', 'dir2']
    stats = ServerStats(mock_client, 'my_test_server', 'a/b/c')

    assert stats.server_name == 'my_test_server'
    assert stats.last_size == expected_size1
    assert stats.second_last_size == 0
    assert stats.is_within_tolerance
    assert stats.report == '- Server: my_test_server, healthy: Yes, last backup size: 1.0 GiB, 2nd last backup size: 0 Bytes.'


def test_server_report_generation_missing_current_backup():
    expected_size2 = 2 ** 20
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size2
    mock_client.get_last_backup_folders.return_value = BackupStatus.NO_CURRENT_BACKUP, ['dir1', 'dir2']
    stats = ServerStats(mock_client, 'my_test_server', 'a/b/c')

    assert stats.server_name == 'my_test_server'
    assert stats.last_size == 0
    assert stats.second_last_size == expected_size2
    assert not stats.is_within_tolerance
    assert stats.report == '- Server: my_test_server, healthy: No, last backup size: 0 Bytes, 2nd last backup size: 1.0 MiB.'


def test_server_report_generation_outside_tolerance():
    expected_size1, expected_size2 = 2 ** 20, 2 ** 30  # 1 MB
    mock_client = mock.Mock()
    mock_client.get_backup_size.side_effect = [expected_size1, expected_size2]
    mock_client.get_last_backup_folders.return_value = BackupStatus.OK, ['dir1', 'dir2']
    stats = ServerStats(mock_client, 'my_test_server', 'a/b/c')

    assert stats.server_name == 'my_test_server'
    assert stats.last_size == expected_size1
    assert stats.second_last_size == expected_size2
    assert not stats.is_within_tolerance
    assert stats.report == '- Server: my_test_server, healthy: No, last backup size: 1.0 MiB, 2nd last backup size: 1.0 GiB.'


def test_server_report_generation_happy_path():
    expected_size = 2 ** 20  # 1 MB
    mock_client = mock.Mock()
    mock_client.get_backup_size.return_value = expected_size
    mock_client.get_last_backup_folders.return_value = BackupStatus.OK, ['dir1', 'dir2']
    stats = ServerStats(mock_client, 'my_test_server', 'a/b/c')

    assert stats.server_name == 'my_test_server'
    assert stats.last_size == expected_size
    assert stats.second_last_size == expected_size
    assert stats.is_within_tolerance
    assert stats.report == '- Server: my_test_server, healthy: Yes, last backup size: 1.0 MiB, 2nd last backup size: 1.0 MiB.'
