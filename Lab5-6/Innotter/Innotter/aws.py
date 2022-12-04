import boto3
from Innotter.settings import AWS

s3_client = boto3.client('s3',
                         endpoint_url=AWS['AWS_ENDPOINT_URL'],
                         aws_access_key_id=AWS['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=AWS['AWS_SECRET_ACCESS_KEY'],
                         region_name=AWS['AWS_DEFAULT_REGION'])

ses = boto3.client('ses',
                   endpoint_url=AWS['AWS_ENDPOINT_URL'],
                   aws_access_key_id=AWS['AWS_ACCESS_KEY_ID'],
                   aws_secret_access_key=AWS['AWS_SECRET_ACCESS_KEY'],
                   region_name=AWS['AWS_DEFAULT_REGION'])
