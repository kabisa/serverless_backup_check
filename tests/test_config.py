import pytest
import backup.config as config


def test_loading_of_non_existent_config():
    with pytest.raises(FileNotFoundError):
        config.load('tests/fixtures/missing_config.yaml')


def test_loading_with_missing_params():
    with pytest.raises(KeyError):
        config.load('tests/fixtures/bad_config.yaml')


def test_loading_of_config():
    backup_cfg = config.load('tests/fixtures/example_config.yaml')
    assert backup_cfg.s3_bucket == 'my_test_bucket'
    assert backup_cfg.folders == ['a', 'b', 'c']
    assert backup_cfg.email_address == 'test@example.com'
