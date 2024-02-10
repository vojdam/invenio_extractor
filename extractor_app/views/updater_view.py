from flask import Blueprint, render_template

from extractor_app.metadata_extractor import MetadataExtractor as ME

from .. import db

bp = Blueprint("updater_view", __name__)


@bp.route("/update")
def update():
    me = ME()
    db.create_custom_data_table()
    return render_template("updater.html", update_db=me.loop_through_instances)
