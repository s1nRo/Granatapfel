from pydantic.main import BaseModel

from mirror.syncer.config_dump import ReleaseAsset


class RepoReleases(BaseModel):
      assets: list[ReleaseAsset]
      max_stored: int