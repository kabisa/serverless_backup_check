
import datetime
from enum import Enum

import boto3


class BackupStatus(Enum):
    OK = 'Ok'
    NO_PREVIOUS_BACKUP = 'Missing previous backup'
    NO_CURRENT_BACKUP = 'Missing current backup'


def date_to_prefix(prefix, date):
    '''Converts a date to a S3 prefix of the form: prefix/year.month.day.
    Month and day are prepended with a leading zero if it is only 1 letter long.
    '''
    return '/'.join([prefix, f'{date.year}.{date.month:02}.{date.day:02}'])


def obj_key_iterator(s3_bucket_name, prefix):
    'Creates a generator for iterating over keys in a folder of an S3 bucket.'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix, Delimiter='/'):
        yield obj.key


def get_first_matching_obj_key(s3_bucket_name, prefix):
    '''Tries to return the first matching object key based on prefix in an S3 bucket.
    Returns None if no matching objects were found.
    '''
    for obj_key in obj_key_iterator(s3_bucket_name, prefix):
        if obj_key.startswith(prefix):
            return obj_key
    return None


def get_backup_prefix_keys(s3_bucket_name, prefix):
    '''Computes the prefixes that should only match a single backup folder in the S3 bucket.
    Returns tuple containing (backup_today_key, backup_yesterday_key).
    '''
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    today_prefix = date_to_prefix(prefix, today)
    yesterday_prefix = date_to_prefix(prefix, yesterday)
    backup_today_key = get_first_matching_obj_key(s3_bucket_name, today_prefix)
    backup_yesterday_key = get_first_matching_obj_key(s3_bucket_name, yesterday_prefix)
    return backup_today_key, backup_yesterday_key


class S3Client(object):
    def __init__(self, s3_bucket_name):
        self.client = boto3.client('s3')
        self.s3_bucket_name = s3_bucket_name

    def get_backup_size(self, backup_folder):
        'Returns the size of bytes of the contents of last backup folder.'
        bytecount = 0
        for obj_key in obj_key_iterator(self.s3_bucket_name, backup_folder):
            filename = '/'.join([backup_folder, obj_key])
            obj_metadata = self.client.head_object(Bucket=self.s3_bucket_name, Key=filename)
            bytecount += obj_metadata.get('ContentLength', 0)
        return bytecount

    def get_last_backup_folders(self, backup_folder):
        '''Function that finds the directories of last 2 backups in a list.
        First element is latest backup (today), second is the backup before that (yesterday).

        Returns tuple of the form (BackupStatus, [backup_folders])
        '''
        backup_today_key, backup_yesterday_key = get_backup_prefix_keys(self.s3_bucket_name,
                                                                        backup_folder)
        result = [backup_today_key, backup_yesterday_key]

        if backup_today_key and backup_yesterday_key:
            return BackupStatus.OK, result
        elif backup_today_key:
            return BackupStatus.NO_PREVIOUS_BACKUP, result
        else:  # if missing backup_today_key
            return BackupStatus.NO_CURRENT_BACKUP, result
