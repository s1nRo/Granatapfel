import asyncio

from jinja2 import Template

from mirror.api.schemas import AppState, home_page
from mirror.config import settings
from mirror.syncer.config_dump import config_dump


async def get_home_page() -> str:
    config = settings.CONFIG_PATH
    config_list = await asyncio.to_thread(config_dump, config)
    repos = ((item["slug"], item["slug"]) for item in config_list)

    return await asyncio.to_thread(home_page, repos)


async def directory_page(state: AppState, owner: str, repo: str) -> Template:
    obj = await asyncio.to_thread(
        state.s3_client.s3.list_objects_v2, Bucket=settings.BUCKET_NAME, Prefix=repo
    )

    iter_obj = (
        (f"{owner}/{repo}/{item['Key']}", item["Key"]) for item in obj["Contents"]
    )
    return await asyncio.to_thread(home_page, iter_obj)


async def download_page(state: AppState, key: str) -> None:
    return await asyncio.to_thread(
        state.s3_client.download_file, bucket_name=settings.BUCKET_NAME, keys=key
    )
