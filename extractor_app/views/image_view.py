from flask import Blueprint, render_template

import base64
from io import BytesIO


from PIL import Image

import numpy

import pydicom


bp = Blueprint("image_view", __name__)


def slice_image(px_array: numpy.ndarray, number_of_slices: int) -> list:
    """Slices a given DICOM image into a desired number of horizontal slices"""
    slice_size = int(len(px_array) / number_of_slices)
    next_slice_border = slice_size
    previous_last_row = 0
    img_list = []

    for row_index in range(len(px_array)):
        if row_index == next_slice_border - 1:
            slice_array = px_array[previous_last_row:row_index]
            next_slice_border = row_index + slice_size
            previous_last_row = row_index
            img = Image.fromarray(slice_array)
            img_list.append(img)
    return img_list


def image_slices_to_string(img_list: list) -> list:
    """Converts a list of PIL image slices to a list of image strings"""
    str_list = []
    for item in img_list:
        image_io = BytesIO()
        item.save(image_io, "PNG")
        data = base64.b64encode(image_io.getvalue()).decode("ascii")
        str_list.append(f"data:image/png;base64,{data}")
    return str_list


@bp.get("/image_view/<folder>/<image_filename>")
def image_viewer(folder: str, image_filename: str):
    # TODO: change to read from config
    path = f"instance\\images\\{folder}\\{image_filename}"
    dataset = pydicom.dcmread(path)
    number_of_slices = 5
    px_array = dataset.pixel_array
    image_slices = slice_image(px_array, number_of_slices)
    string_list = image_slices_to_string(image_slices)
    return render_template(
        "image_view.html", images=string_list, img_height=len(px_array)
    )
