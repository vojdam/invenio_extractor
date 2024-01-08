from flask import Blueprint, render_template

from .. import db


bp = Blueprint("metadata_view", __name__)


@bp.get("/")
def home():
    """base.html homepage that lists all files"""

    database = db.get_db()

    session_list = database.execute("SELECT * FROM SpecimenSession").fetchall()

    max_folder_id = database.execute(
        "SELECT MAX(FolderID) FROM SpecimenSession"
    ).fetchall()

    unique_headers = database.execute(
        "SELECT DISTINCT FolderID, PatientName, PatientID, StudyDate, PatientBirthDate FROM SpecimenSession"
    ).fetchall()

    if max_folder_id[0][0] == None:
        print(max_folder_id[0][0])
        return render_template(
            "base.html", session_list=[[]], max_folder_id=[[0]], unique_headers=[[0]]
        )
    else:
        return render_template(
            "base.html",
            session_list=session_list,
            max_folder_id=max_folder_id,
            unique_headers=unique_headers,
        )


@bp.get("/<int:item_id>")
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

    return render_template(
        "item_view.html",
        item_SpecimenSession=item_SpecimenSession,
        item_SpecimenDescriptionSequence=item_SpecimenDescriptionSequence,
        item_PrimaryAnatomicStructureSequence=item_PrimaryAnatomicStructureSequence,
    )
