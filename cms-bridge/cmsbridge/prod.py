from pathlib import Path

from cmsbridge.config import ProductionDefaultConfig
from cmsbridge.factory import create_app

DEFAULT_CONFIG_FILE = str(Path(__file__).parent.parent / "config" / "prod.json")


def start(config_file: str = DEFAULT_CONFIG_FILE):
    return create_app(ProductionDefaultConfig, config_file)
