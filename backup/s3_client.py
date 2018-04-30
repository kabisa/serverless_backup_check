
from enum import Enum


class BackupStatus(Enum):
    OK = 'Ok'
    NO_PREVIOUS_BACKUP = 'Missing previous backup'
    NO_CURRENT_BACKUP = 'Missing current backup'


