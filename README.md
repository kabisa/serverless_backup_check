
# Serverless backup summary

This repo contains code for posting a mail summary each week about backups, made in a specific S3 bucket.
It uses the serverless framework + Lambda in order to do this.

This assumes that all backups are located in same bucket (or script can be run multiple times with different config).
Layout of files looks as follows:

- S3 bucket
    - path/to/backup/folder
        - 2018.04.26
            - file1
            - file2
            - ...
            - fileN
        - 2018.04.25
        - ...

The script then performs the check to see if the backups from today (if available) are same as ones from last time,
and if they are within tolerance (X% difference per day).

Backup size change limitations are based on the calculations in 
https://drive.google.com/open?id=1tiQXgoRs9gfTeVeEpIu1l0TDDkTfh4dDDm1Eud0zhxQ

# Deploying

make sure you have access to the AWS acount: `kabisa-backups`

```bash
aws-vault exec kabisa-backups --
sls deploy
```

# Adding more buckets to check

In order to do backup checks we need access to the specific backup bucket.
In case the bucket is in a different account you need to grant this access both in the account that owns the bucket as well as the `kabisa-backups` account (for the lambda function) itself.
The access for the execution role of the lambda function on the `kabisa-backups` account side is managed by serverless.yaml. So there you will need to append the last two lines to the policy section of serverless.yaml:

```yaml
      Resource:
        - "... other buckets ..."
        - "arn:aws:s3:::<BUCKET_NAME>"
        - "arn:aws:s3:::<BUCKET_NAME>/*"
```

This policy needs to be added to the account that hosts the s3 bucket:

```json
{
    "Sid": "AllowBackupCheck",
    "Effect": "Allow",
    "Principal": {
        "AWS": "arn:aws:iam::190384451510:role/serverless-backup-analysis-dev-eu-west-1-lambdaRole"
    },
    "Action": "s3:ListBucket",
    "Resource": [
        "arn:aws:s3:::<BUCKET_NAME>",
        "arn:aws:s3:::<BUCKET_NAME>/*"
    ]
}
```