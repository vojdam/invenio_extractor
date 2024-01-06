import os

from flask import Flask, render_template


def create_app(test_config=None):
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

    @app.get("/")
    def home():
        database = db.get_db()
        session_list = database.execute("SELECT * FROM SpecimenSession").fetchall()
        print(session_list)
        return render_template("base.html", session_list=session_list)

    return app
