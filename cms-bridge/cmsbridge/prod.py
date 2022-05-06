from pathlib import Path
from cmsbridge.factory import create_app
from cmsbridge.config import ProductionDefaultConfig

DEFAULT_CONFIG_FILE = str(Path(__file__).parent.parent / "config" / "prod.json")

def start(config_file: str = DEFAULT_CONFIG_FILE):
    return create_app(ProductionDefaultConfig, config_file)
