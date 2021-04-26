import logging
import os
from flask import Flask
from dashboard.blueprints import home, api


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    application_settings_file = os.getenv('APPLICATION_SETTINGS_FILE')

    logger.info(f"Application settings file={application_settings_file}")

    if application_settings_file:
        app.config.from_envvar('APPLICATION_SETTINGS_FILE')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(home.blueprint)
    app.register_blueprint(api.blueprint)

    return app
