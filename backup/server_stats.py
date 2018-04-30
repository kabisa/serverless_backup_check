
import humanize
from backup.s3_client import BackupStatus


def within_tolerance(current, previous):
    'Checks if the backup size is within tolerance compared to last time (+- 10%).'
    return current <= previous * 1.1 and current >= previous * 0.9


def format_backup_size(backup_size):
    '''Formats the size of a backup folder in a human readable format.

    e.g. 1048576 => 1MB

    Returns the backup size as a human readable string
    '''
    return humanize.naturalsize(backup_size, binary=True)


class ServerStats(object):

    def __init__(self, s3_client, server_name, folder):
        self.server_name = server_name
        self.last_size = 0
        self.second_last_size = 0
        self.is_within_tolerance = False

        status, backup_folders = s3_client.get_last_backup_folders(folder)
        if status == BackupStatus.NO_PREVIOUS_BACKUP:
            self.last_size = s3_client.get_backup_size(backup_folders[0])
            self.is_within_tolerance = True
        elif status == BackupStatus.NO_CURRENT_BACKUP:
            self.second_last_size = s3_client.get_backup_size(backup_folders[1])
            self.is_within_tolerance = False
        else:  # OK
            self.last_size = s3_client.get_backup_size(backup_folders[0])
            self.second_last_size = s3_client.get_backup_size(backup_folders[1])
            self.is_within_tolerance = within_tolerance(self.last_size, self.second_last_size)

    @property
    def report(self):
        'Generates a one-line report of the server status.'
        # TODO use html for formatting into table?
        health_status = 'Yes' if self.is_within_tolerance else 'No'
        last_size = format_backup_size(self.last_size)
        second_last_size = format_backup_size(self.second_last_size)
        return f'- Server: {self.server_name}, healthy: {health_status}, ' \
            + f'last backup size: {last_size}, 2nd last backup size: {second_last_size}.'
