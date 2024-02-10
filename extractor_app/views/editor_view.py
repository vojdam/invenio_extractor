from flask import Blueprint, render_template, request

import sqlite3

from .. import config_handler
from .. import db

bp = Blueprint("editor_view", __name__)


def generate_update_table_query() -> None:
    item_key = request.form["submit_button"]
    item_value = request.form[item_key]
    item_value = item_value.replace("'", "''")
    table_name, item_key_short = item_key.split(":")
    item_id = request.form[f"{table_name}:{table_name}ID"]
    folder_id = request.form[f"{table_name}:FolderID"]
    full_folder_bool = "full_folder" in request.form

    if full_folder_bool:
        query_string = f"UPDATE {table_name} SET {item_key_short} = '{item_value}' WHERE FolderID = {folder_id}"
    else:
        query_string = f"UPDATE {table_name} SET {item_key_short} = '{item_value}' WHERE {table_name}ID = {item_id}"

    print(f"Generated query: {query_string}")
    return query_string


def handle_edits(database):
    cursor = database.cursor()
    cursor.execute(generate_update_table_query())
    database.commit()


@bp.route("/metadata/<int:item_id>/edit", methods=("GET", "POST"))
def editor(item_id: int):
    cf_handler = config_handler.ConfigHandler()
    database_path = cf_handler.handle_config("PATHS", "PathToDatabase")
    database = db.get_db()

    if request.method == "POST":
        handle_edits(database)

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
