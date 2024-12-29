from PIL import Image
from pydicom import dcmread

import os
import logging

from . import config_handler


class HEImage:
    def __init__(self, path: str) -> None:
        self.path = path
        self.filename = os.path.splitext(os.path.split(path)[-1])[0]
        self.foldername = os.path.split(os.path.split(path)[0])[-1]
        self.px_array = dcmread(self.path).pixel_array
        self.cf_handler = config_handler.ConfigHandler()
        self.base_path = os.path.join("extractor_app", "static", "resources")

    def create_thumbnail(self):
        thumb_path = os.path.join(
            self.base_path, "thumbnails", self.foldername, f"{self.filename}.jpg"
        )
        image_AR_scale = int(
            self.cf_handler.handle_config("VARS", "ThumbnailARScale")[0]
        )
        image = Image.fromarray(self.px_array)
        image_aspect_ratio = image.size[0] / image.size[1]
        image.thumbnail(
            (image_aspect_ratio * image_AR_scale, image_AR_scale / image_aspect_ratio),
            resample=Image.Resampling.NEAREST,
        )
        logging.info(f"Saving thumbnail: {thumb_path}")
        try:
            os.makedirs(os.path.split(thumb_path)[0])
        except FileExistsError:
            pass
        image.save(thumb_path)

    def create_tiff(self):
        tiff_path = os.path.join(
            self.base_path, "tiff", self.foldername, f"{self.filename}.tiff"
        )
        image = Image.fromarray(self.px_array)
        logging.info(f"Saving TIFF image: {tiff_path}")
        try:
            os.makedirs(os.path.split(tiff_path)[0])
        except FileExistsError:
            pass
        image.save(tiff_path)
