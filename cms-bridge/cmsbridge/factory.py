from flask import Flask

from cmsbridge.views import views_bp


def create_app(settings_obj):
    package = __name__.split('.')[0]
    app = Flask(package, instance_relative_config=True)

    app.config.from_object(settings_obj)

    app.register_blueprint(views_bp)

    return app
