from flask import Blueprint, render_template, request

import sqlite3
from .. import db

bp = Blueprint("metadata_view", __name__)


def handle_search(database):
    """queries the database for the search term"""
    table_name, item_key = request.form["key"].split(":")
    item_value = request.form["value"]
    search_session_list = []
    unique_headers = []

    folder_ids = database.execute(
        f'SELECT DISTINCT FolderID FROM {table_name} WHERE {item_key} LIKE "%{item_value}%"'
    )

    for id in folder_ids:
        search_session_list.append(
            database.execute(
                f"SELECT * FROM SpecimenSession WHERE FolderID = {id[0]}"
            ).fetchall()
        )
        unique_headers.append(
            database.execute(
                f"SELECT FolderID, PatientName, PatientID, StudyDate, AccessionNumber FROM SpecimenSession WHERE FolderID = {id[0]} GROUP BY FolderID"
            ).fetchall()[0]
        )
    session_list = [item for row in search_session_list for item in row]
    specimen_description_list = []
    for row in session_list:
        specimen_description_list.append(
            database.execute(
                f"SELECT * FROM SpecimenDescriptionSequence WHERE SpecimenDescriptionSequenceID = {row[0]}"
            ).fetchall()
        )
    return session_list, unique_headers, specimen_description_list


@bp.route("/", methods=("GET", "POST"))
def home():
    """base.html homepage that lists all files"""
    database = db.get_db()

    session_list = database.execute("SELECT * FROM SpecimenSession").fetchall()
    specimen_description_list = database.execute(
        "SELECT * FROM SpecimenDescriptionSequence"
    ).fetchall()

    unique_headers = database.execute(
        "SELECT FolderID, PatientName, PatientID, StudyDate, AccessionNumber FROM SpecimenSession GROUP BY FolderID"
    ).fetchall()

    try:
        custom_data = database.execute("SELECT * FROM CustomData")
        custom_data_colnames = list(map(lambda x: x[0], custom_data.description))[2:]
        if custom_data == []:
            raise sqlite3.OperationalError
    except sqlite3.OperationalError:
        custom_data = [{" ": " "}]
        custom_data_colnames = []

    if request.method == "POST":
        session_list, unique_headers, specimen_description_list = handle_search(
            database
        )

    return render_template(
        "base.html",
        session_list=session_list,
        # max_folder_id=max_folder_id,
        unique_headers=unique_headers,
        specimen_description_list=specimen_description_list,
        custom_data=custom_data_colnames,
    )


@bp.route("/metadata/<int:item_id>/")
def metadata_view_page(item_id: int):
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

    try:
        item_CustomData = database.execute(
            f"SELECT * FROM CustomData WHERE CustomDataID = {item_id}"
        ).fetchall()
        if item_CustomData == []:
            raise sqlite3.OperationalError
    except sqlite3.OperationalError:
        item_CustomData = [{" ": " "}]

    return render_template(
        "item_view.html",
        item_SpecimenSession=item_SpecimenSession,
        item_SpecimenDescriptionSequence=item_SpecimenDescriptionSequence,
        item_PrimaryAnatomicStructureSequence=item_PrimaryAnatomicStructureSequence,
        item_CustomData=item_CustomData,
    )
