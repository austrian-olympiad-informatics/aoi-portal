from pathlib import Path
from aoiportal.factory import create_app
from aoiportal.config import ProductionDefaultConfig

DEFAULT_CONFIG_FILE = str(Path(__file__).parent.parent / "config" / "prod.json")

def start(config_file: str = DEFAULT_CONFIG_FILE):
    return create_app(ProductionDefaultConfig, config_file)
