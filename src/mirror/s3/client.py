import logging

import boto3
from botocore.client import Config
from mypy_boto3_s3 import S3Client

from mirror.config import Settings


logger = logging.getLogger(__name__)


class S3Repository:
    def __init__(self) -> None:
        self.s3: S3Client = boto3.client(
            "s3",
            aws_access_key_id=Settings.KEY_S3,
            aws_secret_access_key=Settings.TOKEN_S3,
            config=Config(signature_version=Settings.VERSION_S3),
        )

    def create_bucket(self, bucket_name: str) -> None:
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} created.")
        except self.s3.exceptions.BucketAlreadyOwnedByYou:
            logger.info(f"Bucket {bucket_name} already exists.")

    def upload_file(self, bucket_name: str, file: str, name_obj_s3: str) -> None:
        self.s3.upload_file(file, bucket_name, name_obj_s3)
        logger.info(f"File uploaded. Bucket: {bucket_name}, file_name: {name_obj_s3}")

    def download_file(self, bucket_name: str, file: str, name_obj_s3: str) -> None:
        self.s3.download_file(bucket_name, name_obj_s3, file)
        logger.info(f"File downloaded. File_name: {name_obj_s3}")

    def list_obj(self, bucket_name: str) -> list[tuple[str, int]]:
        response = self.s3.list_objects_v2(Bucket=bucket_name)
        list_obj = []
        for obj in response.get("Contents", []):
            list_obj.append((obj["Key"], obj["Size"]))
            logger.info(f"- {obj['Key']} ({obj['Size']} bytes)")
        return list_obj

    def delete_obj(self, bucket_name: str, name_obj_s3: str) -> None:
        self.s3.delete_object(Bucket=bucket_name, Key=name_obj_s3)
        logger.info("Object deleted.")

    def delete_bucket(self, bucket_name: str) -> None:
        self.s3.delete_bucket(Bucket=bucket_name)
        logger.info("Bucket deleted.")
