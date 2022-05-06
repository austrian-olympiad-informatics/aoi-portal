import json

from flask import Flask

from cmsbridge.views import views_bp


def create_app(base_config_obj, config_file):
    package = __name__.split('.')[0]
    app = Flask(package, instance_relative_config=True)

    app.config.from_object(base_config_obj)
    app.config.from_file(config_file, load=json.load)

    app.register_blueprint(views_bp)

    return app
