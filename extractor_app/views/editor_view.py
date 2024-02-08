from flask import Blueprint, render_template

import sqlite3

from .. import config_handler
from .. import db

bp = Blueprint("editor_view", __name__)


@bp.route("/metadata/<int:item_id>/edit", methods=("GET", "POST"))
def editor(item_id: int):
    cf_handler = config_handler.ConfigHandler()
    database_path = cf_handler.handle_config("PATHS", "PathToDatabase")

    database = db.get_db()
    item_SpecimenSession = database.execute(
        f"SELECT * FROM SpecimenSession WHERE SpecimenSessionID = {item_id}"
    ).fetchall()
    item_SpecimenDescriptionSequence = database.execute(
        f"SELECT * FROM SpecimenDescriptionSequence WHERE SpecimenDescriptionSequenceID = {item_id}"
    ).fetchall()
    item_PrimaryAnatomicStructureSequence = database.execute(
        f"SELECT * FROM PrimaryAnatomicStructureSequence WHERE PrimaryAnatomicStructureSequenceID = {item_id}"
    ).fetchall()

    return render_template(
        "editor_view.html",
        item_SpecimenSession=item_SpecimenSession,
        item_SpecimenDescriptionSequence=item_SpecimenDescriptionSequence,
        item_PrimaryAnatomicStructureSequence=item_PrimaryAnatomicStructureSequence,
    )
