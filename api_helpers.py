import os
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename
import uuid
from PIL import Image


load_dotenv()

aws_access_key_id = os.environ['aws_access_key_id']
aws_secret_access_key = os.environ['aws_secret_access_key']

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
BUCKET_NAME_LARGE_IMAGES='sharebnb-gmm'
BUCKET_NAME_SMALL_IMAGES='sharebnb-gmm-small-images'


bucket_base_url_large_images = "https://sharebnb-gmm.s3.us-west-1.amazonaws.com/"
bucket_base_url_small_images = "https://sharebnb-gmm-small-images.s3.us-west-1.amazonaws.com/"


def upload_to_aws(file):
    """ Uploads a file to the aws """

    filename = f"{uuid.uuid4()}"

    s3.upload_fileobj(
        file,
        Bucket = BUCKET_NAME_LARGE_IMAGES,
        ExtraArgs={"ContentType": "mimetype"},
        Key = filename
    )
    url = f"{bucket_base_url_large_images}{filename}"

    small_image_file = resize_image(file)

    s3.upload_fileobj(
        small_image_file,
        Bucket = BUCKET_NAME_SMALL_IMAGES,
        ExtraArgs={"ContentType": "mimetype"},
        Key = filename
    )

    return url


def resize_image(file):
    """ Resizes image to height of 140 """

    # need something like with Image.open(blah)
    with Image.open(file) as img: # test this code
        # img = Image.open(file)
        orig_height = int(img.height)
        orig_width = int(img.width)

        # orig_aspect_ratio = orig_height / orig_width

        orig_height_to_140_ratio = orig_height / 140
        new_height = 140
        new_width = int(orig_width / orig_height_to_140_ratio)

        # height needs to be 140
        resized_img = img.resize((new_width, new_height), resample=Image.BICUBIC)
        # resized_img.show()

        return resized_img

