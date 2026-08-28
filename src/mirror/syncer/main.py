import logging
import time

from mirror.config import settings
from mirror.syncer.client import parse_github_release, stream_upload_s3

import schedule

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)


def uplaoder_s3() -> None:
    logger.info("Syncer has started!")
    config = settings.CONFIG_PATH
    links, ref_links = parse_github_release(config)
    stream_upload_s3(links, ref_links)


schedule.every().day.at("12:00").do(uplaoder_s3)


if __name__ == "__main__":
    uplaoder_s3()
    while True:
        schedule.run_pending()
        time.sleep(1)
