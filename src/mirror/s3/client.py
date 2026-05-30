import logging

import boto3
from botocore.client import Config

from mirror.config import Settings


logger = logging.getLogger(__name__)


def get_client() -> boto3.Session:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=Settings.KEY_S3,
        aws_secret_access_key=Settings.TOKEN_S3,
        config=Config(signature_version=Settings.VERSION_S3),
    )
    return s3


def create_bucket(bucket_name: str) -> None:
    s3 = get_client()

    try:
        s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} created.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        logger.info(f"Bucket {bucket_name} already exists.")
