from flask import Blueprint, render_template

import base64
from io import BytesIO
import os

from PIL import Image

import pydicom

from .. import config_handler

bp = Blueprint("thumbnail_view", __name__)


@bp.route("/thumbnail/")
@bp.route("/thumbnail/<folder>/<image_filename>")
def image_viewer(folder: str, image_filename: str):
    cf_handler = config_handler.ConfigHandler()
    path = os.path.join(cf_handler.handle_config('PATHS', 'PathToImagesFolder')[0],folder,image_filename)
    image_AR_scale = int(cf_handler.handle_config("VARS", "ThumbnailARScale")[0])
    dataset = pydicom.dcmread(path)
    image = Image.fromarray(dataset.pixel_array)
    image_aspect_ratio = image.size[0] / image.size[1]
    image.thumbnail(
        (image_aspect_ratio * image_AR_scale, image_AR_scale / image_aspect_ratio),
        resample=Image.Resampling.NEAREST,
    )
    image_io = BytesIO()
    image.save(image_io, "PNG")
    data = base64.b64encode(image_io.getvalue()).decode("ascii")
    return render_template(
        "thumbnail.html",
        image=f"data:image/png;base64,{data}",
    )
