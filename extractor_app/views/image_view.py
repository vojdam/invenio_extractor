from flask import Blueprint, render_template

import base64
from io import BytesIO

from matplotlib.figure import Figure

import pydicom

from .. import db


bp = Blueprint("image_view", __name__)


# consider something else than mpl
@bp.get("/images/<folder>/<image_filename>")
def image_viewer(folder: str, image_filename: str):
    # TODO: change to read from config
    path = f"instance\\images\\{folder}\\{image_filename}"
    dataset = pydicom.dcmread(path)
    fig = Figure()
    ax = fig.subplots()
    ax.imshow(dataset.pixel_array)
    ax.set_axis_off()
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    data = base64.b64encode(buffer.getbuffer()).decode("ascii")
    return render_template("image_view.html", image=f"data:image/png;base64,{data}")
