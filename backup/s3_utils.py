from typing import Iterable

import boto3
from botocore.exceptions import ClientError


def iterate_objects(s3_bucket_name: str, prefix: str) -> Iterable:
    client = boto3.resource("s3")
    bucket = client.Bucket(s3_bucket_name)
    try:
        for obj in bucket.objects.filter(Prefix=prefix):
            yield obj
    except ClientError:
        print(f"Failed to list bucket {s3_bucket_name}")
        raise


def get_backup_size(s3_bucket_name: str, backup_folder: str) -> int:
    """Returns the size of bytes of the contents of last backup folder."""
    byte_count = 0
    for obj in iterate_objects(s3_bucket_name, backup_folder):
        byte_count += obj.size
    return byte_count
