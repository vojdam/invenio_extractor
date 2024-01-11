import os

from flask import Flask


def create_app(test_config: str = None):
    app = Flask(__name__, instance_relative_config=None)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "metadata.sqlite")
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from extractor_app.commands import init_db_command, update_database

    app.cli.add_command(init_db_command)
    app.cli.add_command(update_database)

    from extractor_app.views import metadata_view, image_view

    app.register_blueprint(metadata_view.bp)
    app.register_blueprint(image_view.bp)

    return app
