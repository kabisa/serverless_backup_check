import pytest
import datetime
import unittest.mock as mock
import backup.s3_client as s3_client
from backup.s3_client import BackupStatus, S3Client
from backup.s3_client import date_to_prefix, get_first_matching_obj_key, get_backup_prefix_keys


@pytest.fixture
def s3_client_no_aws():
    bucket_name = 'my_test_bucket'
    client = S3Client(bucket_name)
    client.client = mock.Mock()
    client.client.head_object.return_value = {'ContentLength': 100}
    return client


@pytest.fixture
def prefix_short():
    return 'a/b/c'


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
def matching_key():
    return 'good_'


@pytest.fixture
def bad_key():
    return 'bad_key'


@pytest.fixture
def mock_obj_key_iterator(good_key):
    s3_client.obj_key_iterator = mock.Mock()
    s3_client.obj_key_iterator.return_value = [good_key]
    return s3_client.obj_key_iterator


def test_date_to_prefix(prefix_long):
    jan82017 = datetime.datetime(year=2017, month=1, day=8)
    may12018 = datetime.datetime(year=2018, month=5, day=1)
    sept182020 = datetime.datetime(year=2020, month=9, day=18)
    assert date_to_prefix(prefix_long, jan82017) == '/'.join([prefix_long, '2017.01.08'])
    assert date_to_prefix(prefix_long, may12018) == '/'.join([prefix_long, '2018.05.01'])
    assert date_to_prefix(prefix_long, sept182020) == '/'.join([prefix_long, '2020.09.18'])


def test_get_first_matching_key(bucket_name, mock_obj_key_iterator,
                                good_key, matching_key, bad_key):
    assert get_first_matching_obj_key(bucket_name, good_key) == good_key
    assert get_first_matching_obj_key(bucket_name, matching_key) == good_key
    assert get_first_matching_obj_key(bucket_name, bad_key) is None


def test_get_backup_prefix_keys(bucket_name, prefix_long, mock_obj_key_iterator):
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    key1, key2 = today, yesterday
    full_path1, full_path2 = date_to_prefix(prefix_long, key1), date_to_prefix(prefix_long, key2)
    mock_obj_key_iterator.return_value = [full_path1, full_path2]
    assert get_backup_prefix_keys(bucket_name, prefix_long) == (full_path1, full_path2)


def test_get_backup_size(s3_client_no_aws, mock_obj_key_iterator, prefix_short):
    keys = ['key1', 'key2']
    mock_obj_key_iterator.return_value = keys
    assert s3_client_no_aws.get_backup_size(prefix_short) == 100 * len(keys)


def test_get_last_backup_folders_happy_path(bucket_name, prefix_short,
                                            s3_client_no_aws, mock_obj_key_iterator):
    backup_keys = ['backup_latest', 'backup_previous']
    s3_client.get_first_matching_obj_key = mock.Mock()
    s3_client.get_first_matching_obj_key.side_effect = backup_keys
    expected_result = BackupStatus.OK, backup_keys
    assert s3_client_no_aws.get_last_backup_folders(prefix_short) == expected_result


def test_get_last_backup_folders_missing_current_backup(
        bucket_name, prefix_short, s3_client_no_aws, mock_obj_key_iterator):
    backup_keys = [None, 'backup_previous']
    s3_client.get_first_matching_obj_key = mock.Mock()
    s3_client.get_first_matching_obj_key.side_effect = backup_keys
    expected_result = BackupStatus.NO_CURRENT_BACKUP, backup_keys
    assert s3_client_no_aws.get_last_backup_folders(prefix_short) == expected_result


def test_get_last_backup_folders_missing_previous_backup(
        bucket_name, prefix_short, s3_client_no_aws, mock_obj_key_iterator):
    backup_keys = ['backup_latest', None]
    s3_client.get_first_matching_obj_key = mock.Mock()
    s3_client.get_first_matching_obj_key.side_effect = backup_keys
    expected_result = BackupStatus.NO_PREVIOUS_BACKUP, backup_keys
    assert s3_client_no_aws.get_last_backup_folders(prefix_short) == expected_result
