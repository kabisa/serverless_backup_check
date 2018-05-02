import pytest
import unittest.mock as mock
import backup.s3_client as s3_client
from backup.s3_client import S3Client


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


def test_get_backup_size(s3_client_no_aws, mock_obj_key_iterator, prefix_short):
    keys = ['key1', 'key2']
    mock_obj_key_iterator.return_value = keys
    assert s3_client_no_aws.get_backup_size(prefix_short) == 100 * len(keys)
