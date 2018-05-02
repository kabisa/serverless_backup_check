
import json
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

    def __init__(self, s3_client, folder):
        self.backup_folder = folder
        self.last_size, self.second_last_size = 0, 0
        self.is_within_tolerance = False

        self.status, backup_folders = s3_client.get_last_backup_folders(folder)
        if self.status == BackupStatus.NO_PREVIOUS_BACKUP:
            self.last_size = s3_client.get_backup_size(backup_folders[0])
        elif self.status == BackupStatus.NO_CURRENT_BACKUP:
            self.second_last_size = s3_client.get_backup_size(backup_folders[1])
        else:  # OK
            self.last_size = s3_client.get_backup_size(backup_folders[0])
            self.second_last_size = s3_client.get_backup_size(backup_folders[1])
            self.is_within_tolerance = within_tolerance(self.last_size, self.second_last_size)

    @property
    def json(self):
        'Returns status of the server as a JSON string.'
        if self.status == BackupStatus.OK:
            if self.is_within_tolerance:
                status = "Backup OK."
            else:
                status = f'Backup size is outside tolerance, now: {self.last_size}, '\
                         f'previous: {self.second_last_size}'
        else:
            status = self.status.value

        info = {
            'backup_folder': self.backup_folder,
            'backup_status': status,
            'last_backup_size': self.last_size,
            'previous_backup_size': self.second_last_size,
        }
        return json.dumps(info)
