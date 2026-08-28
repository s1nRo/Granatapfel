from datetime import datetime
from typing import TypeAlias

from mirror.syncer.config_dump import ReleaseAsset


RealeseDataStructure: TypeAlias = dict[str, list[ReleaseAsset]]
NumberReleaseStored: TypeAlias = dict[str, int]
Row: TypeAlias = tuple[str, str, str, str | datetime]
