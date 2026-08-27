import logging
from pathlib import Path
import re

import requests

from mirror.config import settings
from mirror.syncer.config_dump import ReleaseAsset, config_dump
from mirror.s3.client import s3_repo


logger = logging.getLogger(__name__)


def request_github_release(
    config: Path,
) -> tuple[dict[str, list[ReleaseAsset]], dict[str, str]]:
    logger.info("Parse github realese has begun!")
    config_list = config_dump(config)
    res_dict = {}
    max_rel_stored_dict = {}
    for iter in config_list:
        url = iter["slug"]
        prerel_conf = iter["include_prerel"]
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
            if not prerel_conf and prerel:
                continue
            for asset in item["assets"]:
                if version_of_files is None or version_of_files.search(asset["name"]):
                    meta = ReleaseAsset(
                        file_name=asset["name"],
                        download_url=asset["browser_download_url"],
                        tag=item["tag_name"],
                        published_at=item["published_at"],
                    )
                    release_meta.append(meta)
                    
        res_dict[url] = release_meta
        max_rel_stored_dict[url] = max_rel
        logger.info("Parse github realese has stopped!")
        logger.debug(f"items: {res_dict}, length: {max_rel_stored_dict}")
    return res_dict, max_rel_stored_dict


def stream_upload_s3(
    info_links: dict[str, list[ReleaseAsset]], max_rel_stored_dict: dict[str, int]
) -> None:
    logger.info(f"Uploading in {settings.BUCKET_NAME}")
    for repo_slug, release_meta in info_links.items():
        for asset in release_meta:
            final_key = f"{repo_slug}/{asset.tag}/{asset.file_name}"

            impodence = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=final_key, MaxKeys=1
            )
            if impodence["KeyCount"] > 0:
                logger.info("Skip %s, already in bucket", final_key)
                continue

            res = requests.get(asset.download_url, stream=True)
            s3_repo.upload_file(res.raw, settings.BUCKET_NAME, final_key, asset.published_at)
            logger.info("File: %s uploaded", final_key)

        check_list = s3_repo.s3.list_objects_v2(
            Bucket=settings.BUCKET_NAME, Prefix=repo_slug
        )
        key_list = [item["Key"] for item in check_list.get("Contents", [])]

        keep_tags  = []
        for link in release_meta:
            if link[2] not in keep_tags:
                keep_tags.append(link[2])
        keep_tags = set(keep_tags[: max_rel_stored_dict[repo_slug]])

        if not keep_tags:
            logger.warning(f"No releases for {repo_slug}, cleanup skipped")
            continue

        for obj_key in key_list:
            if obj_key.split("/")[2] not in keep_tags:
                s3_repo.delete_obj(settings.BUCKET_NAME, obj_key)
                logger.info("Object deleted: %s", obj_key)