
import boto3


def obj_key_iterator(s3_bucket_name, prefix):
    'Creates a generator for iterating over keys in a folder of an S3 bucket.'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    for obj in bucket.objects.filter(Prefix=prefix):
        yield obj.key


class S3Client(object):
    def __init__(self, s3_bucket_name):
        self.client = boto3.client('s3')
        self.s3_bucket_name = s3_bucket_name

    def get_backup_size(self, backup_folder):
        'Returns the size of bytes of the contents of last backup folder.'
        bytecount = 0
        for obj_key in obj_key_iterator(self.s3_bucket_name, backup_folder):
            obj_metadata = self.client.head_object(Bucket=self.s3_bucket_name, Key=obj_key)
            bytecount += obj_metadata.get('ContentLength', 0)
        return bytecount
