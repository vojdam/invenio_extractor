import pydicom
import shutil  # use to copy files
import tempfile
import os

from . import config_handler


class FileExporter:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.file_extension = os.path.splitext(file_name)[-1]
        cf_handler = config_handler.ConfigHandler()
        (
            self.images_folder_path,
            self.database_path,
        ) = cf_handler.handle_config("PATHS", "PathToImagesFolder", "PathToDatabase")
        self.path_to_resources = "extractor_app/static/resources/"
        if self.file_extension == ".tiff":
            self.full_path = os.path.join(
                self.path_to_resources, "tiff", self.file_name
            )
        else:
            self.full_path = os.path.join(self.images_folder_path, self.file_name)

    # def read_original_file(self, path: str) -> pydicom.FileDataset:
    #     """Reads the specified file using pydicom and returns it"""
    #     with pydicom.dcmread(path) as file:
    #         original_file = file
    #     return original_file

    def create_temporary_file(self) -> str:
        """Creates a temporary file and returns its path"""
        temporary_directory = tempfile.gettempdir()
        temporary_path = os.path.join(
            temporary_directory, os.path.basename(self.file_name)
        )
        shutil.copy(self.full_path, temporary_path)
        return temporary_path

    def serve_file(self, anonymized: bool = False):
        path = self.create_temporary_file()
        if anonymized and self.file_extension == ".dcm":
            self.anonymize_file(path)
        return path

    def anonymize_file(self, path: str) -> None:
        with pydicom.dcmread(path) as file:
            file.PatientName = "anonymous"
            file.PatientBirthDate = " "
            file.save_as(path)


# copy file as tempfile
# edit to anonymize/use different/delete tag values
# use pydicom.save_as() to save the tempfile
# send to a flask template to download
