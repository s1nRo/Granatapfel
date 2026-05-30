from pathlib import Path

import requests

from mirror.config import settings
from mirror.syncer.config_dump import config_dump

config = settings.CONFIG_PATH


def request_github_release(config: Path) -> dict[str, list[list[str]]]:
    config_list = config_dump(config)
    repos = (item["slug"] for item in config_list)
    for url in repos:
        r = requests.get(
            f"https://api.github.com/repos/{url}/releases",
            headers={"Authorization": f"Bearer {settings.GITHUB_TOKEN}"},
        )
        res_dict = {}
        release_meta = []
        for item in r.json():
            for asset in item["assets"]:
                release_meta.append([asset["name"], asset["browser_download_url"]])
        res_dict[url] = release_meta

    return res_dict

