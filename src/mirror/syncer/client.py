import logging
from pathlib import Path

import requests

from mirror.config import settings
from mirror.syncer.config_dump import config_dump
from mirror.s3.client import s3_repo


config = settings.CONFIG_PATH

logger = logging.getLogger(__name__)


def request_github_release(config: Path) -> dict[str, list[list[str]]]:
    config_list = config_dump(config)
    repos = (item["slug"] for item in config_list)
    res_dict = {}
    for url in repos:
        r = requests.get(
            f"https://api.github.com/repos/{url}/releases",
            headers={"Authorization": f"Bearer {settings.GITHUB_TOKEN}"},
        )
        release_meta = []
        for item in r.json():
            for asset in item["assets"]:
                release_meta.append([asset["name"], asset["browser_download_url"]])
        res_dict[url] = release_meta

    return res_dict


def stream_upload_s3(info_links: dict[str, list[list[str]]]) -> None:
    for item in info_links.values():
        for link in item:
            key = link[0]
            url = link[1]

            impodence = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=key, MaxKeys=1
            )
            if key in str(impodence):
                logger.debug("This object is in Bucket.")
                continue
            # print(f"url: {url}, key: {key}")
            res = requests.get(url, stream=True)
            s3_repo.upload_file(res.raw, settings.BUCKET_NAME, key)


if __name__ == "__main__":
    # config = settings.CONFIG_PATH
    # res = request_github_release(config)
    # print(res)
    # stream_upload_s3(res)
    url = "https://github.com/Flowseal/zapret-discord-youtube/releases/download/1.9.9a/zapret-discord-youtube-1.9.9a.zip"
    key = "zapret-discord-youtube-1.9.9a.zip"
    test = "zapret-discord-youtube-1.8.9a.zip"
    # res = requests.get(url, stream=True)
    # s3_repo.upload_file(res.raw, settings.BUCKET_NAME, key)

    impodence = s3_repo.s3.list_objects_v2(Bucket=settings.BUCKET_NAME, Prefix=key)
    if test in str(impodence):
        print("ok")
    else:
        print("fuck!")
