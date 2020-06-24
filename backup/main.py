#!/usr/bin/env python3

import json
import logging
from backup.s3_client import S3Client
from backup.server_stats import ServerStats


logger = logging.getLogger(__name__)


def response_error(error):
    'Helper function to return an error response.'
    logger.error(error)
    return {
        'statusCode': 400,
        'body': error
    }


def handler(event, context):
    logger.info('Received request to do backup check...')
    body = json.loads(event['body'])
    bucket_name = body.get('bucket_name')
    backup_folder = body.get('backup_folder')
    file_date_format = body.get('file_date_format')

    if not bucket_name:
        return response_error(f'Missing `bucket_name` variable in POST body, aborting.')
    if not backup_folder:
        return response_error(f'Missing `backup_folder` variable in POST body, aborting.')

    if file_date_format:
        logger.info(f'Performing backup check, folder: {backup_folder}, file_date_format: {file_date_format}')
    else:
        logger.info(f'Performing backup check, folder: {backup_folder}...')
    s3 = S3Client(bucket_name)
    backup_stats = ServerStats(s3, backup_folder, file_date_format)

    response_body = backup_stats.json
    response = {
        'statusCode': 200,
        'body': response_body
    }

    logger.info(f'Sending back response: {response}.')
    return response
