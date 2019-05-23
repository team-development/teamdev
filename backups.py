import boto3
import botocore
import datetime

def backup(self):
    yaml = YAML()
    self.logger.info("Backing up projects to S3.!")
    foldername = "osdpbackup"
    dt = datetime.datetime.now()
    datestring = dt.strftime('%m_%d_%Y')
    with open(r"osdp/configuration/settings.yml") as f:
        dataMap = yaml.load(f)
        local_directory = os.getcwd()
        mybucket = "osdp-backups-" + dataMap['osdp']['username']
        destination = 'OSDP'
        region = 'us-west-2'
        conn = boto3.resource('s3',region_name="us-west-2")

        if not conn.Bucket(mybucket) in conn.buckets.all():
            print('creating bucket ' + mybucket + '...')
            try:
                conn.create_bucket(Bucket=mybucket, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
            except botocore.exceptions.ClientError as e:
                print('Error: ' + e.response['Error']['Message'])
        else:
            print('bucket ' + mybucket + ' already exists')

        self.zipfolder()
        client = boto3.client('s3')
        session = boto3.Session(region_name='us-west-2')
        s3 = session.resource('s3')
        s3bucket = s3.Bucket(mybucket)
        s3.Bucket(mybucket).upload_file('osdpbackup.zip', "osdp" + "/" + datestring + "/" + "osdpbackup.zip")

