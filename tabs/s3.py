import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket="tabs-flask", object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True


def delete_file(file_name, bucket="tabs-flask"):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.delete_object(Bucket=bucket, Key=file_name)
    except ClientError as e:
        print(e)
        return False
    return True

