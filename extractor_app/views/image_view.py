from flask import Blueprint, render_template

import base64
from io import BytesIO

from PIL import Image
from .. import pydicom_PIL

import pydicom


bp = Blueprint("image_view", __name__)


# consider something else than mpl
@bp.get("/images/<folder>/<image_filename>")
def image_viewer(folder: str, image_filename: str):
    # TODO: change to read from config
    path = f"instance\\images\\{folder}\\{image_filename}"
    dataset = pydicom.dcmread(path)
    image = pydicom_PIL.get_PIL_image(dataset)
    image_aspect_ratio = image.size[0] / image.size[1]
    image.thumbnail(
        (image_aspect_ratio * 130, 130 / image_aspect_ratio),
        resample=Image.Resampling.NEAREST,
    )
    # fig = Figure()
    # ax = fig.subplots()
    # ax.imshow(dataset.pixel_array)
    # ax.set_axis_off()
    image_io = BytesIO()
    # fig.savefig(buffer, format="png", bbox_inches="tight")
    image.save(image_io, "PNG")
    data = base64.b64encode(image_io.getvalue()).decode("ascii")
    return render_template(
        "image_view.html",
        image=f"data:image/png;base64,{data}",
    )
