from math import ceil
import sqlite3

from flask import Blueprint, abort, jsonify, render_template, request, url_for

from .. import db

bp = Blueprint("metadata_view", __name__)

DEFAULT_FOLDER_PAGE_SIZE = 100
DEFAULT_SESSION_PAGE_SIZE = 100
MAX_PAGE_SIZE = 200

BASE_SEARCH_FIELDS = {
    "SpecimenSession:PatientName": ("SpecimenSession", "PatientName"),
    "PrimaryAnatomicStructureSequence:CodeMeaning": (
        "PrimaryAnatomicStructureSequence",
        "CodeMeaning",
    ),
    "SpecimenSession:PatientID": ("SpecimenSession", "PatientID"),
    "SpecimenSession:AccessionNumber": ("SpecimenSession", "AccessionNumber"),
    "SpecimenSession:StudyDate": ("SpecimenSession", "StudyDate"),
}


def _quote_identifier(identifier: str) -> str:
    """Quote a validated SQLite identifier."""
    return '"' + identifier.replace('"', '""') + '"'


def _positive_int_arg(name: str, default: int, maximum: int | None = None) -> int:
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        value = default

    value = max(1, value)
    if maximum is not None:
        value = min(value, maximum)
    return value


def _custom_data_columns(database) -> list[str]:
    """Return user-defined CustomData columns, excluding primary/foreign keys."""
    try:
        rows = database.execute("PRAGMA table_info(CustomData)").fetchall()
    except sqlite3.OperationalError:
        return []

    if not rows:
        return []

    return [row[1] for row in rows if row[1] not in {"CustomDataID", "FolderID"}]


def _allowed_search_fields(database) -> dict[str, tuple[str, str]]:
    fields = dict(BASE_SEARCH_FIELDS)
    for column in _custom_data_columns(database):
        fields[f"CustomData:{column}"] = ("CustomData", column)
    return fields


def _search_filter(database, search_key: str, search_value: str) -> tuple[str, list]:
    """Build a validated folder-level search filter and its SQL parameters."""
    if not search_key or not search_value:
        return "", []

    allowed_fields = _allowed_search_fields(database)
    if search_key not in allowed_fields:
        abort(400, description="Invalid search field")

    table_name, column_name = allowed_fields[search_key]
    table_sql = _quote_identifier(table_name)
    column_sql = _quote_identifier(column_name)

    return (
        f"WHERE FolderID IN ("
        f"SELECT DISTINCT FolderID FROM {table_sql} "
        f"WHERE {column_sql} LIKE ?"
        f")",
        [f"%{search_value}%"],
    )


def _get_folder_page(
    database, search_key: str, search_value: str, page: int, per_page: int
):
    where_sql, params = _search_filter(database, search_key, search_value)

    total = database.execute(
        f"SELECT COUNT(DISTINCT FolderID) FROM SpecimenSession {where_sql}", params
    ).fetchone()[0]

    total_pages = max(1, ceil(total / per_page)) if total else 1
    page = min(page, total_pages)
    offset = (page - 1) * per_page

    headers = database.execute(
        f"""
        SELECT FolderID, PatientName, PatientID, StudyDate, AccessionNumber
        FROM SpecimenSession
        {where_sql}
        GROUP BY FolderID
        ORDER BY StudyDate DESC, FolderID DESC
        LIMIT ? OFFSET ?
        """,
        [*params, per_page, offset],
    ).fetchall()

    return headers, total, page, total_pages


@bp.route("/", methods=("GET",))
def home():
    """Metadata viewer with server-side folder pagination and lazy-loaded sessions."""
    database = db.get_db()

    page = _positive_int_arg("page", 1)
    per_page = _positive_int_arg(
        "per_page", DEFAULT_FOLDER_PAGE_SIZE, maximum=MAX_PAGE_SIZE
    )
    search_key = request.args.get("key", "").strip()
    search_value = request.args.get("value", "").strip()

    unique_headers, total_folders, page, total_pages = _get_folder_page(
        database, search_key, search_value, page, per_page
    )
    custom_data_colnames = _custom_data_columns(database)

    first_item = (page - 1) * per_page + 1 if total_folders else 0
    last_item = min(page * per_page, total_folders)

    return render_template(
        "base.html",
        unique_headers=unique_headers,
        custom_data=custom_data_colnames,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_folders=total_folders,
        first_item=first_item,
        last_item=last_item,
        search_key=search_key,
        search_value=search_value,
    )


@bp.route("/api/folder_sessions", methods=("GET",))
def folder_sessions():
    """Return one page of image/session rows for a selected folder."""
    database = db.get_db()

    try:
        folder_id = int(request.args["folder_id"])
    except (KeyError, TypeError, ValueError):
        abort(400, description="folder_id must be an integer")

    page = _positive_int_arg("page", 1)
    per_page = _positive_int_arg(
        "per_page", DEFAULT_SESSION_PAGE_SIZE, maximum=MAX_PAGE_SIZE
    )
    offset = (page - 1) * per_page

    total = database.execute(
        "SELECT COUNT(*) FROM SpecimenSession WHERE FolderID = ?", (folder_id,)
    ).fetchone()[0]

    rows = database.execute(
        """
        SELECT
            ss.SpecimenSessionID,
            ss.FolderID,
            ss.PatientName,
            ss.ImageID,
            ss.PhotometricInterpretation,
            ss.ContainerIdentifier,
            sds.SpecimenShortDescription
        FROM SpecimenSession AS ss
        LEFT JOIN SpecimenDescriptionSequence AS sds
            ON sds.SpecimenDescriptionSequenceID = ss.SpecimenSessionID
        WHERE ss.FolderID = ?
        ORDER BY ss.SpecimenSessionID
        LIMIT ? OFFSET ?
        """,
        (folder_id, per_page, offset),
    ).fetchall()

    items = []
    for row in rows:
        patient_name = row["PatientName"] or ""
        items.append(
            {
                "SpecimenSessionID": row["SpecimenSessionID"],
                "PatientName": patient_name[12:],
                "ImageID": row["ImageID"] or "",
                "Color": "RGB"
                if row["PhotometricInterpretation"] == "RGB"
                else "B/W",
                "ContainerIdentifier": row["ContainerIdentifier"] or "",
                "SpecimenShortDescription": row["SpecimenShortDescription"] or "",
                "metadata_url": url_for(
                    "metadata_view.metadata_view_page",
                    item_id=row["SpecimenSessionID"],
                ),
            }
        )

    return jsonify(
        {
            "folder_id": folder_id,
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "has_more": offset + len(items) < total,
        }
    )


@bp.route("/metadata/<int:item_id>/")
def metadata_view_page(item_id: int):
    database = db.get_db()
    item_SpecimenSession = database.execute(
        "SELECT * FROM SpecimenSession WHERE SpecimenSessionID = ?", (item_id,)
    ).fetchall()
    item_SpecimenDescriptionSequence = database.execute(
        "SELECT * FROM SpecimenDescriptionSequence WHERE SpecimenDescriptionSequenceID = ?",
        (item_id,),
    ).fetchall()
    item_PrimaryAnatomicStructureSequence = database.execute(
        "SELECT * FROM PrimaryAnatomicStructureSequence WHERE PrimaryAnatomicStructureSequenceID = ?",
        (item_id,),
    ).fetchall()

    if not item_SpecimenSession:
        abort(404)

    try:
<<<<<<< HEAD
        folder_id = item_SpecimenSession[0]["FolderID"]
        item_CustomData = database.execute(
            "SELECT * FROM CustomData WHERE FolderID = ?", (folder_id,)
=======
        folder_id = item_SpecimenSession[0][1]
        item_CustomData = database.execute(
            f"SELECT * FROM CustomData WHERE FolderID = {folder_id}"
>>>>>>> ca747b774273c1bcc618189e7b0cfb981f0777b8
        ).fetchall()
        if not item_CustomData:
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
