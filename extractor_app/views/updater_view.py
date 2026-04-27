from flask import Blueprint, render_template

from extractor_app.metadata_extractor import MetadataExtractor as ME

from .. import db

bp = Blueprint("updater_view", __name__)


@bp.route("/update", methods=["POST"])
def update():
    db.create_custom_data_table()
    me = ME()
    me.loop_through_instances()
    return render_template("updater.html")
