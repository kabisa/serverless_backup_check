
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

Before deploying the lambda function, environment needs to setup for the lambda.
This can be done by providing an environment.sh file in the root directory of this repo with the following structure:

```
export BUCKET_NAME=XXX
```

BUCKET_NAME must be the name of the bucket that contains the backups.

After this is done, you can deploy with the following command: `make deploy`.

Backup size change limitations are based on the calculations in 
https://drive.google.com/open?id=1tiQXgoRs9gfTeVeEpIu1l0TDDkTfh4dDDm1Eud0zhxQ
