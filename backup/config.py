
import yaml


def load(file_name):
    'Parses YAML configuration data, returns config as an object.'
    with open(file_name, 'r') as yaml_file:
        data = yaml.load(yaml_file)
    s3_bucket = data['s3_bucket_name']
    email_address = data['email_address']
    folders = data['backup_folders']
    return BackupConfig(s3_bucket, folders, email_address)


class BackupConfig(object):

    def __init__(self, s3_bucket, folders, email_address):
        self.s3_bucket = s3_bucket
        self.folders = folders
        self.email_address = email_address
