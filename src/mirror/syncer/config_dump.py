from pathlib import Path

import yaml

from mirror.config import settings


def config_dump(config_path: Path) -> list[dict[str, str]]:
    with open(config_path, "r") as f:
        config: dict[str, list[dict[str, str]]] = yaml.load(f, Loader=yaml.SafeLoader)

    return config["repos"]


if __name__ == "__main__":
    config = settings.CONFIG_PATH
    print(config_dump(config))
