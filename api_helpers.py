import os
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename

load_dotenv()

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
BUCKET_NAME='sharebnb-gmm'

bucket_base_url = "https://sharebnb-gmm.s3.us-west-1.amazonaws.com/"


def upload_to_aws(file):
    """ Uploads a file to the aws """
    filename = secure_filename(file.filename)

    s3.upload_fileobj(
        file,
        Bucket = BUCKET_NAME,
        ExtraArgs={"ContentType": "mimetype"},
        Key = filename
    )
    url = f"{bucket_base_url}{filename}"

    # TODO: refactor this later so it doesnt have to save to os.

    return url