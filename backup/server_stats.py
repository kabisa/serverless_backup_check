
import json
import datetime
import humanize


def within_tolerance(current, previous):
    'Checks if the backup size is within tolerance compared to last time (+- 10%).'
    return current <= previous * 1.1 and current >= previous * 0.9


def date_to_prefix(prefix, date):
    '''Converts a date to a S3 prefix of the form: prefix/year.month.day.
    Month and day are prepended with a leading zero if it is only 1 letter long.
    '''
    return '/'.join([prefix, f'{date.year}.{date.month:02}.{date.day:02}'])


def format_backup_size(backup_size):
    '''Formats the size of a backup folder in a human readable format.

    e.g. 1048576 => 1MB

    Returns the backup size as a human readable string
    '''
    return humanize.naturalsize(backup_size, binary=True)


def get_backup_prefix_keys(prefix):
    '''Computes the prefixes that should only match a single backup folder in the S3 bucket.
    Returns tuple containing (backup_today_prefix, backup_yesterday_prefix).
    '''
    today = datetime.datetime.today()
    one_day_ago = today - datetime.timedelta(days=1)
    two_days_ago = today - datetime.timedelta(days=2)
    backup_one_day_prefix = date_to_prefix(prefix, one_day_ago)
    backup_two_days_prefix = date_to_prefix(prefix, two_days_ago)
    return backup_one_day_prefix, backup_two_days_prefix


class ServerStats(object):

    def __init__(self, s3_client, folder):
        self.backup_folder = folder
        backup_folders = get_backup_prefix_keys(folder)
        self.last_size = s3_client.get_backup_size(backup_folders[0])
        self.second_last_size = s3_client.get_backup_size(backup_folders[1])

    @property
    def status(self):
        if self.last_size == 0 and self.second_last_size == 0:
            return 'Missing current and previous backup'
        elif self.second_last_size == 0:
            return 'Missing previous backup'
        elif self.last_size == 0:
            return 'Missing current backup'
        elif not within_tolerance(self.last_size, self.second_last_size):
            return f'Backup size is outside tolerance'

        return 'Backup OK'

    @property
    def json(self):
        'Returns status of the server as a JSON string.'
        info = {
            'backup_folder': self.backup_folder,
            'backup_status': self.status,
            'last_backup_size': self.last_size,
            'previous_backup_size': self.second_last_size,
        }
        return json.dumps(info)
