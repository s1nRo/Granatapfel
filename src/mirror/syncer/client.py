import logging
from pathlib import Path
import re

from packaging import version
import requests

from mirror.config import settings
from mirror.syncer.config_dump import config_dump
from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)


def request_github_release(config: Path) -> tuple[dict[str, list[list[str]]], dict[str, str]]:
    logger.info("Parse github realese has begun!")
    config_list = config_dump(config)
    res_dict = {}
    max_rel_stored_dict = {}
    for iter in config_list:
        url = iter["slug"]
        prerel_conf = iter["prerel"]
        rule = iter.get("asset_regexp")
        version_of_files = re.compile(rule) if rule else None
        max_rel = iter["max_rel_stored"]
        r = requests.get(
            f"https://api.github.com/repos/{url}/releases",
            headers={"Authorization": f"Bearer {settings.GITHUB_TOKEN}"},
            params={"per_page": max_rel},
        )
        release_meta = []
        for item in r.json():
            prerel = item.get("prerelease")
            if prerel_conf == "false" and prerel == "true":
                continue
            for asset in item["assets"]:
                if version_of_files is None or version_of_files.search(asset["name"]):
                    release_meta.append(
                        [asset["name"], asset["browser_download_url"], item["tag_name"]]
                    )
        res_dict[url] = release_meta
        max_rel_stored_dict[url] = max_rel
        logger.info("Parse github realese has stopped!")
        logger.debug(f"items: {res_dict}, length: {max_rel_stored_dict}")
    return res_dict, max_rel_stored_dict


def stream_upload_s3(
    info_links: dict[str, list[list[str]]], max_rel_stored_dict: dict[str, int]
) -> None:
    logger.info("Uploading in S3 has begun!")
    for item in info_links.items():
        for link in item[1]:
            key = link[0]
            url = link[1]
            tag = link[2]

            final_key = f"{item[0]}/{tag}/{key}"

            impodence = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=final_key, MaxKeys=1
            )
            if impodence["KeyCount"] > 0:
                logger.info("This object is in Bucket.")
                continue

            res = requests.get(url, stream=True)
            s3_repo.upload_file(res.raw, settings.BUCKET_NAME, final_key)
            logger.info(
                f"This file:{final_key} has uploaded to bucket:{settings.BUCKET_NAME}."
            )
        
        check_key = item[0]
        logger.info(f"Updating items:{check_key} in S3!")
        check_list = s3_repo.s3.list_objects_v2(
            Bucket=settings.BUCKET_NAME, Prefix=check_key
        )
        key_list = [item["Key"] for item in check_list.get("Contents", [])]

        version_list = []
        for item in key_list:
            key_str = item.split("/")
            version_list.append(f"{key_str[0]}/{key_str[1]}/{key_str[2]}")
        version_list = list(set(version_list))

        sorted_version_list = sorted(
            version_list, key=lambda x: version.parse(x.split("/")[2])
        )

        len_s3_storage = len(sorted_version_list)
        logger.debug(f"length of s3: {len_s3_storage}")
        len_max_storage = max_rel_stored_dict[check_key]
        logger.debug(f"length by config: {len_s3_storage}")
        diff_del_version = abs(len_s3_storage - len_max_storage)

        if diff_del_version != 0:
            for i in range(diff_del_version):
                del_version = sorted_version_list[i]
                for item in key_list:
                    if del_version in item:
                        s3_repo.delete_obj(settings.BUCKET_NAME, item)
                        logger.info("Object deleted!")
