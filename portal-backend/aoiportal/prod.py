from aoiportal.factory import create_app
from aoiportal.config import ProductionDefaultConfig

def start():
    return create_app(ProductionDefaultConfig, "/config.json")
