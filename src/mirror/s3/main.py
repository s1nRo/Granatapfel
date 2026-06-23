from mirror.config import settings
from mirror.s3.client import s3_repo


if __name__ == "__main__":
    url = "Flowseal/zapret-discord-youtube"
    key = url.split("/")
    obj = s3_repo.s3.list_objects_v2(Bucket=settings.BUCKET_NAME, Prefix=key[1])
    # print(obj)

    obj_content = obj["Contents"]
    print(obj_content)
    iter_obj = [item["Key"] for item in obj_content]
    print(iter_obj)
