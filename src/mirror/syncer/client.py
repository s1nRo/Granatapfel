import logging
from pathlib import Path
import re

import requests
from requests.exceptions import HTTPError, RequestException

from mirror.aliases import NumberReleaseStored, RealeseDataStructure
from mirror.config import settings
from mirror.s3.client import S3Repository
from mirror.syncer.config_dump import ReleaseAsset, config_dump


logger = logging.getLogger(__name__)


def _request_to_github(url: str, parse_number: int) -> requests.Response:
    for _ in range(settings.ATTEMPTS):
        request = requests.get(
            f"https://api.github.com/repos/{url}/releases",
            headers={"Authorization": f"Bearer {settings.GITHUB_TOKEN}"},
            params={"per_page": parse_number},
            timeout=(5, 30),
        )
        if request.status_code == 200:
            return request
    raise RequestException


def parse_github_release(
    config: Path,
) -> tuple[RealeseDataStructure, NumberReleaseStored]:
    config_list = config_dump(config)
    full_meta_releases: RealeseDataStructure = {}
    num_release_store: NumberReleaseStored = {}

    for iter in config_list:
        url = iter["slug"]
        is_prerelease = iter["include_prerel"]
        ruleset = iter.get("asset_regexp")
        versions = re.compile(ruleset) if ruleset else None
        max_num_release = int(iter["max_rel_stored"])

        try:
            request = _request_to_github(url, max_num_release)
        except RequestException as e:
            logger.error("Failed to request github, %s", e)
            continue

        release_meta: list[ReleaseAsset] = []

        for item in request.json():
            prerelease = item.get("prerelease")
            if not is_prerelease and prerelease:
                continue
            for asset in item["assets"]:
                if versions is None or versions.search(asset["name"]):
                    meta = ReleaseAsset(
                        file_name=asset["name"],
                        download_url=asset["browser_download_url"],
                        tag=item["tag_name"],
                        published_at=item["published_at"],
                    )
                    release_meta.append(meta)

        full_meta_releases[url] = release_meta
        num_release_store[url] = max_num_release
        logger.debug("items: %s, length: %s", full_meta_releases, num_release_store)
    return full_meta_releases, num_release_store


def stream_upload_s3(s3_repo: S3Repository,
    meta: RealeseDataStructure, num_release_store: NumberReleaseStored
) -> None:
    logger.info("Uploading in %s", settings.BUCKET_NAME)
    for repo_slug, release_meta in meta.items():
        for asset in release_meta:
            final_key = f"{repo_slug}/{asset.tag}/{asset.file_name}"

            impodence = s3_repo.s3.list_objects_v2(
                Bucket=settings.BUCKET_NAME, Prefix=final_key, MaxKeys=1
            )
            if impodence["KeyCount"] > 0:
                logger.info("Skip %s, already in bucket", final_key)
                continue
            try:
                res = requests.get(asset.download_url, timeout=(5, 60), stream=True)
                res.raise_for_status()
                res.raw.decode_content = True
            except RequestException as e:
                logger.error("A request error occurred %s:", e)
                continue
        
            s3_repo.upload_file(
                res.raw, settings.BUCKET_NAME, final_key, asset.published_at
            )
            logger.info("File: %s uploaded", final_key)

        check_list = s3_repo.list_keys(
            bucket=settings.BUCKET_NAME, prefix=repo_slug
        )
        
        key_list: list[tuple[str, str]] = []
        for item in check_list:
            key = item.get("Key", "")
            parts = key.split("/")
            if len(parts) != 4:
                logger.warning("Unexpected key layout, skipping: %s", key)
                continue
                
            _, _, tag, _ = parts
            key_list.append((key, tag))
            
        keep_tags: list[str] = []

        for link in release_meta:
            if link.tag not in keep_tags:
                keep_tags.append(link.tag)
        unique_tags: set[str] = set(keep_tags[: num_release_store[repo_slug]])

        if not unique_tags:
            logger.warning("No releases for %s, cleanup skipped", repo_slug)
            continue

        for obj_key, tag in key_list:
            if tag not in unique_tags:
                s3_repo.delete_obj(settings.BUCKET_NAME, obj_key)
                logger.info("Object deleted: %s", obj_key)
