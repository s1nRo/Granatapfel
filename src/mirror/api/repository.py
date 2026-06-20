import asyncio
import logging

from fastapi import logger
from jinja2 import Template

from mirror.api.schemas import AppState, home_page
from mirror.config import settings
from mirror.syncer.config_dump import config_dump

from packaging import version

logger = logging.getLogger(__name__)


async def get_home_page() -> str:
    config = settings.CONFIG_PATH
    config_list = await asyncio.to_thread(config_dump, config)
    repos = ((item["slug"], item["slug"]) for item in config_list)

    return await asyncio.to_thread(home_page, repos)


async def directory_page(
    state: AppState, owner: str, repo: str, version: str
) -> Template:

    extraction_key = f"{owner}/{repo}/{version}"
    obj = await asyncio.to_thread(
        state.s3_client.s3.list_objects_v2,
        Bucket=settings.BUCKET_NAME,
        Prefix=extraction_key,
    )

    iter_obj = (
        (item["Key"], item["Key"].split("/")[3]) for item in obj.get("Contents", [])
    )
    return await asyncio.to_thread(home_page, iter_obj)


async def version_page(state: AppState, owner: str, repo: str) -> Template:

    extraction_key = f"{owner}/{repo}"
    obj = await asyncio.to_thread(
        state.s3_client.s3.list_objects_v2,
        Bucket=settings.BUCKET_NAME,
        Prefix=extraction_key,
    )
    key_list = [item["Key"] for item in obj.get("Contents", [])]

    key_list_unique = []
    for item in key_list:
        key_str = item.split("/")
        key_list_unique.append(f"{key_str[0]}/{key_str[1]}/{key_str[2]}")

    key_list_unique = set(key_list_unique)

    sorted_key_list = sorted(
        key_list_unique, key=lambda x: version.parse(x.split("/")[2]), reverse=True
    )
    print(key_list_unique)
    iter_obj = ((item, item.split("/")[2]) for item in sorted_key_list)
    return await asyncio.to_thread(home_page, iter_obj)


async def download_page(
    state: AppState, owner: str, repo: str, version: str, key: str
) -> None:
    extraction_key = f"{owner}/{repo}/{version}/{key}"
    return await asyncio.to_thread(
        state.s3_client.download_file,
        bucket_name=settings.BUCKET_NAME,
        keys=extraction_key,
    )
