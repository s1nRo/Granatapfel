from pathlib import Path

import yaml


def config_dump(config_path: Path) -> list[dict[str, str]]:
    with open(config_path, "r") as f:
        config: dict[str, list[dict[str, str]]] = yaml.load(f, Loader=yaml.SafeLoader)

    return config["repos"]
