from pathlib import Path

from aoiportal.config import ProductionDefaultConfig
from aoiportal.factory import create_app

DEFAULT_CONFIG_FILE = str(Path(__file__).parent.parent / "config" / "prod.json")


def start(config_file: str = DEFAULT_CONFIG_FILE):
    return create_app(ProductionDefaultConfig, config_file)
