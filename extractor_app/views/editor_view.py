from flask import Blueprint, render_template, request

import sqlite3

from .. import config_handler
from .. import db

bp = Blueprint("editor_view", __name__)


def generate_update_table_query(cursor) -> None:
    item_key = request.form["submit_button"]
    item_value = request.form[item_key]
    item_value = item_value.replace("'", "''")
    table_name, item_key_short = item_key.split(":")
    item_id = request.form[f"{table_name}:{table_name}ID"]
    folder_id = request.form[f"{table_name}:FolderID"]
    full_folder_bool = "full_folder" in request.form

    # handle custom data
    if (
        table_name == "CustomData"
        and len(
            cursor.execute(
                f"SELECT CustomDataID FROM CustomData WHERE CustomDataID = {item_id}"
            ).fetchall()
        )
        == 0
    ):
        query_string = f"INSERT INTO CustomData(CustomDataID, FolderID, {item_key_short}) VALUES ({item_id}, {folder_id}, '{item_value}')"
        print(f"Generated query: {query_string}")
        cursor.execute(query_string)
        if full_folder_bool:
            all_item_ids_in_folder = cursor.execute(
                f"SELECT SpecimenSessionID FROM SpecimenSession WHERE FolderID = {folder_id}"
            ).fetchall()
            for id in all_item_ids_in_folder:
                if str(id[0]) == item_id:
                    continue
                query_string = f"INSERT INTO CustomData(CustomDataID, FolderID, {item_key_short}) VALUES ({id[0]}, {folder_id}, '{item_value}')"
                print(f"Generated query: {query_string}")
                try:
                    cursor.execute(query_string)
                except sqlite3.IntegrityError:
                    cursor.execute(
                        f"UPDATE {table_name} SET {item_key_short} = '{item_value}' WHERE {table_name}ID = {folder_id}"
                    )

    else:
        if full_folder_bool:
            query_string = f"UPDATE {table_name} SET {item_key_short} = '{item_value}' WHERE FolderID = {folder_id}"
        else:
            query_string = f"UPDATE {table_name} SET {item_key_short} = '{item_value}' WHERE {table_name}ID = {item_id}"
        print(f"Generated query: {query_string}")
        cursor.execute(query_string)


def handle_edits(database):
    cursor = database.cursor()
    generate_update_table_query(cursor)
    database.commit()


@bp.route("/metadata/<int:item_id>/edit", methods=("GET", "POST"))
def editor(item_id: int):
    cf_handler = config_handler.ConfigHandler()
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

    try:
        item_CustomData = database.execute(
            f"SELECT * FROM CustomData WHERE CustomDataID = {item_id}"
        ).fetchall()
        if item_CustomData == []:
            raise sqlite3.OperationalError
    except sqlite3.OperationalError:
        try:
            cur = database.execute(f"SELECT * FROM CustomData")
            item_CustomData = list(map(lambda x: x[0], cur.description))
            item_CustomData = [
                dict(zip(item_CustomData, ("" for x in range(len(item_CustomData)))))
            ]
        except sqlite3.OperationalError:
            item_CustomData = [{" ": " "}]

    return render_template(
        "editor_view.html",
        item_SpecimenSession=item_SpecimenSession,
        item_SpecimenDescriptionSequence=item_SpecimenDescriptionSequence,
        item_PrimaryAnatomicStructureSequence=item_PrimaryAnatomicStructureSequence,
        item_CustomData=item_CustomData,
    )
