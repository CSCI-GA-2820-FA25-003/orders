# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import os
import sys
from flask_cors import CORS
from flask import Flask
from service import config
from service.common import log_handlers
from service.models.order import Order


############################################################
# Initialize the Flask instance
############################################################


def set_static_config(app):
    """Set the static config for the application."""
    with open(
        os.path.join(app.root_path, "static", "assets", "config.js"),
        "w",
        encoding="utf-8",
    ) as f:
        url = os.getenv("API_URL", "http://localhost:8000")
        f.write(f"window._env_ = {{ API_URL: '{url}' }};")
    app.logger.info(f"Static config set to {url}")


def create_app():
    """Initialize the core application."""
    # Create Flask application
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(config)
    set_static_config(app)
    # Enable CORS for all routes
    CORS(app)
    # Initialize Plugins
    # pylint: disable=import-outside-toplevel
    from service.models.order import db

    db.init_app(app)

    with app.app_context():
        # Dependencies require we import the routes AFTER the Flask app is created
        # pylint: disable=wrong-import-position, wrong-import-order, unused-import
        from service import routes  # noqa: F401 E402
        from service.common import error_handlers, cli_commands  # noqa: F401, E402

        try:
            db.create_all()
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            # gunicorn requires exit code 4 to stop spawning workers when they die
            sys.exit(4)

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        return app
