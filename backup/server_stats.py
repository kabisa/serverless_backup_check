import json
from datetime import date, timedelta
import humanize

from backup.s3_utils import get_backup_size
from backup.size_change_monitor import relative_size_change, allowed_size_change
import os

assert os.sep == "/"


def within_tolerance(current, previous):
    """Checks if the backup size grew less than the allowed size."""
    return relative_size_change(current, previous) <= allowed_size_change(previous)


def date_to_prefix(prefix, date, file_date_format):
    """
    Converts a date to a S3 prefix of the form: prefix/year.month.day.
    Month and day are prepended with a leading zero if it is only 1 letter long.
    """
    if not file_date_format:
        file_date_format = "%Y.%m.%d"
    if prefix is None:
        raise ValueError("Prefix is not allowed to be None")
    return os.path.join(prefix, date.strftime(file_date_format))


def format_backup_size(backup_size):
    """
    Formats the size of a backup folder in a human readable format.

    e.g. 1048576 => 1MB

    Returns the backup size as a human readable string
    """
    return humanize.naturalsize(backup_size, binary=True)


def get_backup_prefix_keys(prefix, file_date_format):
    """
    Computes the prefixes that should only match a single backup folder in the S3 bucket.
    Returns tuple containing (backup_today_prefix, backup_yesterday_prefix).
    """
    today = date.today()
    one_day_ago = today - timedelta(1)
    two_days_ago = today - timedelta(2)
    backup_one_day_prefix = date_to_prefix(prefix, one_day_ago, file_date_format)
    backup_two_days_prefix = date_to_prefix(prefix, two_days_ago, file_date_format)
    return backup_one_day_prefix, backup_two_days_prefix


class ServerStats(object):
    def __init__(self, bucket_name, folder, file_date_format=None):
        self.bucket_name = bucket_name
        self.backup_folder = folder
        backup_folders = get_backup_prefix_keys(folder, file_date_format)
        self.last_size = get_backup_size(bucket_name, backup_folders[0])
        self.second_last_size = get_backup_size(bucket_name, backup_folders[1])

    @property
    def one_day_ago(self):
        return (date.today() - timedelta(1)).strftime("%Y-%m-%d")

    @property
    def two_days_ago(self):
        return (date.today() - timedelta(2)).strftime("%Y-%m-%d")

    @property
    def status(self):
        if self.last_size == 0 and self.second_last_size == 0:
            return f"Missing backup from {self.one_day_ago} and {self.two_days_ago}"
        elif self.second_last_size == 0:
            return f"Missing backup from {self.two_days_ago}"
        elif self.last_size == 0:
            return f"Missing backup from {self.one_day_ago}"
        elif not within_tolerance(self.last_size, self.second_last_size):
            return f"Backup size is outside tolerance"

        return "Backup OK"

    @property
    def json(self):
        """Returns status of the server as a JSON string."""
        info = {
            "backup_folder": self.backup_folder,
            "backup_status": self.status,
            "last_backup_size": format_backup_size(self.last_size),
            "last_backup_date": self.one_day_ago,
            "previous_backup_size": format_backup_size(self.second_last_size),
            "previous_backup_date": self.two_days_ago,
        }
        return json.dumps(info, sort_keys=True)
