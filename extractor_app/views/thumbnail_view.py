from flask import Blueprint, render_template

import base64
from io import BytesIO

from PIL import Image

import pydicom

from .. import config_handler

bp = Blueprint("thumbnail_view", __name__)


# consider something else than mpl
@bp.get("/thumbnail/<folder>/<image_filename>")
def image_viewer(folder: str, image_filename: str):
    cf_handler = config_handler.ConfigHandler()
    path = f"{cf_handler.handle_config('PATHS', 'PathToImagesFolder')[0]}/{folder}/{image_filename}"
    dataset = pydicom.dcmread(path)
    image = Image.fromarray(dataset.pixel_array)
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
        "thumbnail.html",
        image=f"data:image/png;base64,{data}",
    )
