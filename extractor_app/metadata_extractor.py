from pydicom import dcmread
from pydicom.datadict import dictionary_keyword
import os
import logging
import sqlite3
from . import config_handler
from natsort import os_sorted
from . import image_generator


class MetadataExtractor:
    def __init__(self) -> None:
        cf_handler = config_handler.ConfigHandler()
        database_path, images_path = cf_handler.handle_config(
            "PATHS", "PathToDatabase", "PathToImagesFolder"
        )

        self.database_path = cf_handler.resolve_project_path(database_path)
        self.path_to_dicom_folders = cf_handler.resolve_project_path(images_path)

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(level=logging.INFO)
        self.sql_string_SpecimenSession = """INSERT INTO SpecimenSession (SpecificCharacterSet, ImageType, SOPClassUID, 
            SOPInstanceUID, StudyDate, SeriesDate, StudyTime, SeriesTime, AccessionNumber, 
            Modality, Manufacturer, ReferringPhysicianName, StudyDescription, SeriesDescription, 
            InstitutionalDepartmentName, NameOfPhysiciansReadingStudy, ManufacturerModelName, 
            PatientName, PatientID, PatientBirthDate, PatientSex, ClinicalTrialSponsorName, 
            ClinicalTrialProtocolID, ClinicalTrialSiteName, ClinicalTrialSubjectID, 
            DeviceSerialNumber, SoftwareVersions, ProtocolName, StudyInstanceUID, 
            SeriesInstanceUID, StudyID, SeriesNumber, InstanceNumber, PatientOrientation, 
            SamplesPerPixel, PhotometricInterpretation, Rows, Columns, BitsAllocated, 
            BitsStored, HighBit, PixelRepresentation, LossyImageCompression, ContainerIdentifier, 
            IssuerOfTheContainerIdentifierSequence, ContainerTypeCodeSequence, 
            AcquisitionContextSequence, FolderID, ImageID, ImageFileName)
            VALUES
            (:SpecificCharacterSet, :ImageType, :SOPClassUID, 
            :SOPInstanceUID, :StudyDate, :SeriesDate, :StudyTime, :SeriesTime, :AccessionNumber, 
            :Modality, :Manufacturer, :ReferringPhysicianName, :StudyDescription, :SeriesDescription, 
            :InstitutionalDepartmentName, :NameOfPhysiciansReadingStudy, :ManufacturerModelName, 
            :PatientName, :PatientID, :PatientBirthDate, :PatientSex, :ClinicalTrialSponsorName, 
            :ClinicalTrialProtocolID, :ClinicalTrialSiteName, :ClinicalTrialSubjectID, 
            :DeviceSerialNumber, :SoftwareVersions, :ProtocolName, :StudyInstanceUID, 
            :SeriesInstanceUID, :StudyID, :SeriesNumber, :InstanceNumber, :PatientOrientation, 
            :SamplesPerPixel, :PhotometricInterpretation, :Rows, :Columns, :BitsAllocated, 
            :BitsStored, :HighBit, :PixelRepresentation, :LossyImageCompression, 
            :ContainerIdentifier, :IssuerOfTheContainerIdentifierSequence, 
            :ContainerTypeCodeSequence, :AcquisitionContextSequence, :FolderID, :ImageID, :ImageFileName)"""
        self.sql_string_SpecimenDescriptionSequence = """INSERT INTO SpecimenDescriptionSequence
            (SpecimenIdentifier, SpecimenUID, IssuerOfTheSpecimenIdentifierSequence, 
            SpecimenShortDescription, SpecimenPreparationSequence, FolderID) 
            VALUES 
            (:SpecimenIdentifier, :SpecimenUID, :IssuerOfTheSpecimenIdentifierSequence, 
            :SpecimenShortDescription, :SpecimenPreparationSequence, :FolderID)"""
        self.sql_string_PrimaryAnatomicStructureSequence = """INSERT INTO PrimaryAnatomicStructureSequence
            (CodeValue, CodingSchemeDesignator, CodeMeaning, FolderID) 
            VALUES 
            (:CodeValue, :CodingSchemeDesignator, :CodeMeaning, :FolderID)"""

    def _get_metadata(self, folder_path: str) -> list:
        """Saves metadata from a DCM file folder to a list of dicts"""
        full_folder_path = os.path.join(self.path_to_dicom_folders, folder_path)
        files_in_folder = os.listdir(full_folder_path)
        dict_meta_list = []
        for file in os_sorted(files_in_folder):
            if not file.endswith(".dcm"):
                continue
            try:
                with dcmread(
                    os.path.join(full_folder_path, file), stop_before_pixels=True
                ) as dcm_file:
                    dict_meta = dcm_file.to_json_dict()
            except Exception as e:
                logging.warning(
                    "Failed to read DICOM file: %s. Error: %s", file, str(e)
                )
                continue
            if "00400560" not in dict_meta: # check if SpecimenDescriptionSequence is present, if not, then it's a non-extracted file
                continue
            if file[6] == "_":
                dict_meta["ImageID"] = file[:6]
            else:
                dict_meta["ImageID"] = file[:7]
            dict_meta["ImageFileName"] = file
            dict_meta_list.append(dict_meta)
        return dict_meta_list

    def format_date(self, date: str) -> str:
        """Formats date from yyyymmdd to yyyy-mm-dd"""
        return f"{date[:4]}-{date[4:6]}-{date[6:]}"

    def _translate_codes(self, full_dict: dict) -> dict:
        """Translates the DICOM codes to their respective strings"""
        all_keys = full_dict.keys()
        new_all_keys = []
        for key in all_keys:
            if key == "ImageID" or key == "ImageFileName":
                new_all_keys.append(key)
                continue
            new_all_keys.append(dictionary_keyword(key))
            # check for nested dicts
            if (
                type(full_dict[key]) is dict
                and full_dict[key].get("vr") == "SQ"
                and not full_dict[key].get("Value") == []
            ):
                nested_dict = self._translate_codes(full_dict[key]["Value"][0])
                full_dict[key] = nested_dict
        return dict(zip(new_all_keys, full_dict.values()))

    def loop_through_instances(self, force_renew: bool = False) -> None:
        """Loops through folders in the DICOM images folder and performs metadata extraction"""
        if force_renew:
            folders = os.listdir(self.path_to_dicom_folders)
            folder_id = 1
        else:
            folders, folder_id = self._check_for_changes()
            if folders == os.listdir(self.path_to_dicom_folders):
                folder_id = 1
        with sqlite3.connect(self.database_path) as database:
            for folder in folders:
                logging.info(f"Starting metadata extraction out of folder: {folder}")
                try:
                    full_meta = self._get_metadata(folder)
                except NotADirectoryError:
                    continue


                for dictionary in full_meta:
                    translated_dictionary = self._translate_codes(dictionary)
                    if (
                        translated_dictionary["PhotometricInterpretation"].get("Value")[
                            0
                        ]
                        == "RGB"
                    ):
                        try:
                            self.generate_thumb_and_tiff(
                                os.path.join(
                                    self.path_to_dicom_folders,
                                    folder,
                                    translated_dictionary["ImageFileName"],
                                ),
                                translated_dictionary["Rows"].get("Value")[0] == 496
                                and translated_dictionary["Columns"].get("Value")[0] == 496,
                            )
                        except Exception as e:
                            logging.warning(
                                "Failed to generate thumbnail and tiff for image: %s. Error: %s",
                                translated_dictionary["ImageFileName"],
                                str(e),
                            )

                    # write to db:
                    self.write_to_database(
                        database,
                        translated_dictionary,
                        self.sql_string_SpecimenSession,
                        folder_id,
                        "SpecimenSession",
                    )
                    self.write_to_database(
                        database,
                        translated_dictionary["SpecimenDescriptionSequence"],
                        self.sql_string_SpecimenDescriptionSequence,
                        folder_id,
                        "SpecimenDescriptionSequence",
                    )
                    self.write_to_database(
                        database,
                        translated_dictionary["SpecimenDescriptionSequence"][
                            "PrimaryAnatomicStructureSequence"
                        ],
                        self.sql_string_PrimaryAnatomicStructureSequence,
                        folder_id,
                        "PrimaryAnatomicStructureSequence",
                    )
                folder_id += 1
        logging.info("Metadata saved successfully!")

    def generate_thumb_and_tiff(self, img_path: str, only_thumb: bool = True) -> None:
        img = image_generator.HEImage(img_path)
        img.create_thumbnail()
        if not only_thumb:
            img.create_tiff()

    def _check_for_changes(self):
        """Compares written image folders and available image folders"""
        with sqlite3.connect(self.database_path) as database:
            cursor = database.cursor()
            written_folders_sql = cursor.execute(
                "SELECT DISTINCT StudyInstanceUID FROM SpecimenSession"
            ).fetchall()

            max_folder_id = database.execute(
                "SELECT MAX(FolderID) FROM SpecimenSession"
            ).fetchall()
        written_folders = [folder[0][:] for folder in written_folders_sql]
        if max_folder_id[0][0] is None:
            max_folder_id_int = 0
        else:
            max_folder_id_int = int(max_folder_id[0][0])
        available_folders = os.listdir(self.path_to_dicom_folders)
        folder_difference = [
            folder for folder in available_folders if folder not in written_folders
        ]
        return folder_difference, max_folder_id_int + 1

    def write_to_database(
        self,
        database: sqlite3.Connection,
        meta_dict: dict,
        sql_string: str,
        folder_id: int,
        table_name: str,
    ) -> None:
        """Write to a SQL database"""
        new_values = []
        for key, value in meta_dict.items():
            if key == "ImageID" or key == "ImageFileName":
                new_values.append(value)
                continue
            new_values.append(
                str(value.get("Value", " "))
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace("{", "")
                .replace("}", "")
                .replace("^", " ")
            )
        meta_dict = dict(zip(meta_dict.keys(), new_values))
        meta_dict["FolderID"] = folder_id
        # format dates:
        if "PatientBirthDate" in meta_dict:
            meta_dict["PatientBirthDate"] = self.format_date(
                meta_dict["PatientBirthDate"]
                if len(meta_dict["PatientBirthDate"]) == 8
                else "        "
            )
            meta_dict["StudyDate"] = self.format_date(meta_dict["StudyDate"])
            meta_dict["SeriesDate"] = self.format_date(meta_dict["SeriesDate"])
        cursor = database.cursor()

        try:
            cursor.execute(sql_string, meta_dict)
        except sqlite3.Error:
            logging.exception(
                "Failed while writing table %s. Database path: %s. Metadata keys: %s",
                table_name,
                self.database_path,
                sorted(meta_dict.keys()),
            )
            raise


# TESTING
# metadata_ext = MetadataExtractor("extractor_app\config.ini")
# metadata_ext.loop_through_instances()
