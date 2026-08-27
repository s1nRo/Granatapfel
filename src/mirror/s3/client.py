from io import BytesIO
import logging

import boto3
from botocore.client import ClientError, Config
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import FileobjTypeDef

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
            logger.info(f"Bucket {bucket_name} is existed.")
        except ClientError:
            logger.error(f"Bucket {bucket_name} isn't created.")

    def upload_file(self, data: FileobjTypeDef, bucket_name: str, keys: str, published_at: str | None = None) -> None:
        extra = {'Metadata': {'published-at': published_at}} if published_at else None

        self.s3.upload_fileobj(
            data, bucket_name, keys,
            ExtraArgs=extra            
        )
        logger.info(f"File uploaded. Bucket: {bucket_name}, file_name: {keys}")

    def download_file(self, bucket_name: str, keys: str) -> bytes:
        response = self.s3.get_object(Bucket=bucket_name, Key=keys)

        logger.info(f"File downloaded. File_name: {keys}")
        return response

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


s3_repo = S3Repository()
