import logging
from pathlib import Path
import re

from packaging import version
import requests

from mirror.config import settings
from mirror.syncer.config_dump import config_dump
from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)


def request_github_release(config: Path) -> dict[str, list[list[str]]]:
    config_list = config_dump(config)
    print(config_list)
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
    return res_dict, max_rel_stored_dict


def stream_upload_s3(info_links: dict[str, list[list[str]]], max_rel_stored_dict: dict[str, int]) -> None:
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
                continue

            res = requests.get(url, stream=True)
            s3_repo.upload_file(res.raw, settings.BUCKET_NAME, final_key)
            logger.info(
                f"This file:{final_key} has uploaded to bucket:{settings.BUCKET_NAME}."
            )
        check_key = item[0]
        print(check_key)
        check_list = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=check_key
            )
        key_list = [item["Key"] for item in check_list.get("Contents", [])]

        version_list = []
        for item in key_list:
            key_str = item.split("/")
            version_list.append(f"{key_str[0]}/{key_str[1]}/{key_str[2]}")
        version_list = list(set(version_list))
        print(version_list)

        sorted_version_list = sorted(
        version_list, key=lambda x: version.parse(x.split("/")[2])
        )

        len_s3_storage = len(sorted_version_list)
        len_max_storage = max_rel_stored_dict[check_key]
        diff_del_version = abs(len_s3_storage - len_max_storage)
        print(diff_del_version)

        if diff_del_version != 0:
            print("obj has to be del!")
            for i in range(diff_del_version):
                del_version = sorted_version_list[i]
                print(del_version)
                for item in key_list:
                    print(item)
                    if del_version in item:
                        print(item.split("/")[1])
                        s3_repo.delete_obj(settings.BUCKET_NAME, item)
                        print("obj del!")

    
if __name__ == "__main__":
    config = settings.CONFIG_PATH
    lis, ver_lis = request_github_release(config)
    print(ver_lis)
    stream_upload_s3(lis, ver_lis)
    # print(lis)

    # stream_upload_s3(lis)
    # extraction_key = f"2dust/v2rayN"
    # obj = s3_repo.s3.list_objects_v2(Bucket=settings.BUCKET_NAME, Prefix=extraction_key)
    # print(obj)
