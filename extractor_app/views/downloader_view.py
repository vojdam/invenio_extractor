from flask import Blueprint, send_file, request
import os

from .. import db

from .. import file_exporter

bp = Blueprint("downloader_view", __name__)


@bp.route("/metadata/<int:item_id>/download")
def downloader(item_id: int):
    database = db.get_db()
    anonymize = request.args.get("anonymize")
    tiff = request.args.get("tiff")
    filename_sql = database.execute(
        f"SELECT StudyInstanceUID, ImageFileName FROM SpecimenSession WHERE SpecimenSessionID = {item_id}"
    ).fetchone()
    filename = "/".join(filename_sql)
    if tiff:
        filename = f"{os.path.splitext(filename)[0]}.tiff"
    fe = file_exporter.FileExporter(filename)
    tmp = fe.serve_file(anonymized=anonymize)
    print(f"Serving file: {filename}")
    return send_file(tmp, download_name=os.path.basename(filename))
