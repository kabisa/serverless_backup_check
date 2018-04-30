#!/usr/bin/env python3


import os
import sys
import logging
import mail

logger = logging.getLogger(__name__)


def do_backup_check(bucket_name, folders):
    pass


def main():
    backup_folders = os.environ.get('BACKUP_FOLDERS')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    email = os.environ.get('EMAIL_ADDRESS')

    for env_var, var in [('BACKUP_FOLDERS', backup_folders),
                         ('S3_BUCKET_NAME', bucket_name),
                         ('EMAIL_ADDRESS', email)]:
        if not var:
            logger.error(f'Missing `{env_var}` environment variable, aborting.')
            sys.exit(1)

    logger.info('Performing backup check...')
    backup_summary = do_backup_check(bucket_name, backup_folders)

    logger.info('Finished backup check! Sending out mail summary...')
    mail.send_backup_summary(backup_summary)

    logger.info('Done!')
    sys.exit(0)


if __name__ == '__main__':
    main()
