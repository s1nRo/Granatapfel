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
                release_meta.append(
                    [asset["name"], asset["browser_download_url"], item["tag_name"]]
                )
        res_dict[url] = release_meta

    return res_dict


def stream_upload_s3(info_links: dict[str, list[list[str]]]) -> None:
    for item in info_links.items():
        for link in item[1]:
            key = link[0]
            url = link[1]
            tag = link[2]
            print(f"key:{key}; url:{url}; tag:{tag}")

            final_key = f"{item[0]}/{tag}/{key}"
            print(f"key: {final_key}")

            impodence = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=final_key, MaxKeys=1
            )
            print(impodence)
            if impodence["KeyCount"] > 0:
                logger.info("This object is in Bucket.")
                break

            res = requests.get(url, stream=True)
            s3_repo.upload_file(res.raw, settings.BUCKET_NAME, final_key)
            logger.info(
                f"This file:{final_key} has uploaded to bucket:{settings.BUCKET_NAME}."
            )


if __name__ == "__main__":
    config = settings.CONFIG_PATH
    lis = request_github_release(config)
    stream_upload_s3(lis)
    # extraction_key = f"2dust/v2rayN"
    # obj = s3_repo.s3.list_objects_v2(Bucket=settings.BUCKET_NAME, Prefix=extraction_key)
    # print(obj)
