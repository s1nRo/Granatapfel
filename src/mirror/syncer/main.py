import time

from mirror.config import settings
from mirror.syncer.client import request_github_release, stream_upload_s3

import schedule


def uplaoder_s3() -> None:
    config = settings.CONFIG_PATH
    links = request_github_release(config)
    stream_upload_s3(links)


schedule.every().day.at("12:00").do(uplaoder_s3)


if __name__ == "__main__":
    uplaoder_s3()
    while True:
        schedule.run_pending()
        time.sleep(1)
