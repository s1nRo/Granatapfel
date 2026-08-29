import logging

import boto3
from botocore.client import ClientError, Config
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import FileobjTypeDef, GetObjectOutputTypeDef

from mirror.config import settings


logger = logging.getLogger(__name__)


class S3Repository:
    def __init__(self) -> None:
        self.s3: S3Client = boto3.client(
            "s3",
            endpoint_url=settings.S3_URL,
            aws_access_key_id=settings.KEY_S3,
            aws_secret_access_key=settings.TOKEN_S3,
            config=Config(signature_version=settings.VERSION_S3),
        )
        self.check_if_existed(bucket_name=settings.BUCKET_NAME)

    def check_if_existed(self, bucket_name: str) -> None:
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError:
            logger.error("Bucket %s isn't created", bucket_name)
            raise
            
        logger.info("Bucket %s exists", bucket_name)

    def upload_file(
        self,
        data: FileobjTypeDef,
        bucket_name: str,
        keys: str,
        published_at: str | None = None,
    ) -> None:
        extra = {"Metadata": {"published-at": published_at}} if published_at else None
        try:
            self.s3.upload_fileobj(data, bucket_name, keys, ExtraArgs=extra)
        except ClientError:
            logger.error("Upload object %s failed in bucket %s",  keys, bucket_name)
            raise

        logger.info("File %s uploaded in bucket: %s", keys, bucket_name)

    def download_file(
        self, bucket_name: str, key: str
    ) -> GetObjectOutputTypeDef | None:
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=key)
        except self.s3.exceptions.NoSuchKey as e:
            logger.error("File %s not found, %s", key, e)
            return None
        except ClientError as e:
            logger.error("Failed download %s", e)
            raise

        logger.info("File %s downloaded", key)
        return response

    def delete_obj(self, bucket_name: str, name_obj_s3: str) -> None:
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=name_obj_s3)
        except ClientError:
            logger.error("Failed delete object %s in bucket %s", name_obj_s3)
            raise
            
        logger.info("Object %s deleted in bucket %s", name_obj_s3, bucket_name)


s3_repo = S3Repository()
