import asyncio

from jinja2 import Template

from mirror.api.schemas import AppState, home_page
from mirror.config import settings
from mirror.syncer.config_dump import config_dump


async def get_home_page() -> str:
    config = settings.CONFIG_PATH
    config_list = await asyncio.to_thread(config_dump, config)
    repos = (item["slug"] for item in config_list)

    return await asyncio.to_thread(home_page, repos)


async def directory_page(state: AppState, url: str) -> Template:
    obj = asyncio.to_thread(state.s3_client.list_obj, url)
    iter_obj = (item[0] for item in obj)

    return await asyncio.to_thread(home_page, iter_obj)


async def download_page(state: AppState, url: str) -> None:
    return await asyncio.to_thread(state.s3_client.download_file, url)
