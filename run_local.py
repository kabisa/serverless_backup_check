#!/usr/bin/env python3
import json
from typing import Optional

try:
    import fire
except ImportError:
    print("Plz run `pip install fire`")

from botocore.exceptions import NoCredentialsError, ClientError
from backup.server_stats import ServerStats


def main(
    backup_folder: str,
    bucket_name: str = "dovetail-backup-archive",
    file_date_format: Optional[str] = None,
):
    try:
        backup_stats = ServerStats(bucket_name, backup_folder, file_date_format)
    except (NoCredentialsError, ClientError) as ex:
        print(f"Boto error: {ex}\r\n" "Plz run `aws-vault exec dovetail-backups` first")
    else:
        print(json.dumps(backup_stats.json))


if __name__ == "__main__":
    fire.Fire(main)
