import asyncio
import logging
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

from mirror.api.schemas import AppState, home_page
from mirror.config import settings
from mirror.syncer.config_dump import config_dump


logger = logging.getLogger(__name__)

security = HTTPBasic()


def format_bytes(size: int) -> str:
    power = 2**10
    n = 0
    size_casted: float = float(size)
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size_casted > power:
        size_casted /= power
        n += 1
    return f"{round(size_casted, 1)} {power_labels[n]}B"


async def get_home_page() -> str:
    config = settings.CONFIG_PATH
    config_list = await asyncio.to_thread(config_dump, config)
    repos = ((item["slug"], item["slug"], "-", "-") for item in config_list)

    return await asyncio.to_thread(home_page, repos, parent_path="/")


async def directory_page(state: AppState, owner: str, repo: str, version: str) -> str:

    extraction_key = f"{owner}/{repo}/{version}"
    obj = await asyncio.to_thread(
        state.s3_client.s3.list_objects_v2,
        Bucket=settings.BUCKET_NAME,
        Prefix=extraction_key,
    )

    iter_obj = (
        (
            item.get("Key", ""),
            item.get("Key", "").split("/")[3],
            format_bytes(item.get("Size", 0)),
            item.get("LastModified", ""),
        )
        for item in obj.get("Contents", [])
    )
    return await asyncio.to_thread(home_page, iter_obj, parent_path=f"/{owner}/{repo}/")


async def version_page(state: AppState, owner: str, repo: str) -> str:

    extraction_key = f"{owner}/{repo}"
    obj = await asyncio.to_thread(
        state.s3_client.s3.list_objects_v2,
        Bucket=settings.BUCKET_NAME,
        Prefix=extraction_key,
    )
    key_list = [item.get("Key", "") for item in obj.get("Contents", [])]

    keys_unique: dict[str, str] = {}

    for item in key_list:
        key_str = item.split("/")

        head = await asyncio.to_thread(
            state.s3_client.s3.head_object,
            Bucket=settings.BUCKET_NAME,
            Key=item,
        )
        time = head["Metadata"].get("published-at", "")

        keys_unique[f"{key_str[0]}/{key_str[1]}/{key_str[2]}"] = time

    sorted_keys = sorted(keys_unique, key=lambda x: keys_unique[x])
    logger.debug(keys_unique)
    iter_obj = ((item, item.split("/")[2], "-", "-") for item in sorted_keys)
    return await asyncio.to_thread(home_page, iter_obj, parent_path="/")


async def download_page(
    state: AppState, owner: str, repo: str, version: str, key: str
) -> GetObjectOutputTypeDef | None:
    extraction_key = f"{owner}/{repo}/{version}/{key}"
    return await asyncio.to_thread(
        state.s3_client.download_file,
        bucket_name=settings.BUCKET_NAME,
        key=extraction_key,
    )


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = settings.USERNAME_API.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = settings.PASSWORD_API.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
