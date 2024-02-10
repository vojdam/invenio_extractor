from flask import Blueprint, render_template, request

import sqlite3
from .. import db

bp = Blueprint("metadata_view", __name__)


def handle_search(database):
    """queries the database for the search term"""
    item_key = request.form["key"]
    item_value = request.form["value"]

    search_session_list = database.execute(
        f'SELECT * FROM SpecimenSession WHERE {item_key} LIKE "%{item_value}%"'
    ).fetchall()
    unique_headers = database.execute(
        f'SELECT FolderID, PatientName, PatientID, StudyDate, PatientBirthDate FROM SpecimenSession WHERE {item_key} LIKE "%{item_value}%" GROUP BY FolderID'
    ).fetchall()
    specimen_description_list = []
    for row in search_session_list:
        specimen_description_list.append(
            database.execute(
                f"SELECT * FROM SpecimenDescriptionSequence WHERE SpecimenDescriptionSequenceID = {row['SpecimenSessionID']}"
            ).fetchall()
        )
    return search_session_list, unique_headers, specimen_description_list


@bp.route("/", methods=("GET", "POST"))
def home():
    """base.html homepage that lists all files"""
    database = db.get_db()

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
        )

    session_list = database.execute("SELECT * FROM SpecimenSession").fetchall()
    specimen_description_list = database.execute(
        "SELECT * FROM SpecimenDescriptionSequence"
    ).fetchall()

    unique_headers = database.execute(
        "SELECT FolderID, PatientName, PatientID, StudyDate, PatientBirthDate FROM SpecimenSession GROUP BY FolderID"
    ).fetchall()

    return render_template(
        "base.html",
        session_list=session_list,
        # max_folder_id=max_folder_id,
        unique_headers=unique_headers,
        specimen_description_list=specimen_description_list,
    )


@bp.route("/metadata/")
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
