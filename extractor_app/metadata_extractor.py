from pydicom import dcmread
from pydicom.datadict import dictionary_keyword
import os
import logging
import sqlite3
import configparser


class MetadataExtractor:
    def __init__(self, config_path: str) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        (self.database_path, self.path_to_dicom_folders) = self.handle_config()
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
            AcquisitionContextSequence, FolderID)
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
            :ContainerTypeCodeSequence, :AcquisitionContextSequence, :FolderID)"""
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

    def handle_config(self):
        """Reads settings from .ini config file"""
        return [
            self.config["PATHS"]["PathToDatabase"],
            self.config["PATHS"]["PathToImagesFolder"],
        ]

    def _get_metadata(self, folder_path: str) -> list:
        """Saves metadata from a DCM file folder to a list of dicts"""
        full_folder_path = f"{self.path_to_dicom_folders}\{folder_path}"
        files_in_folder = os.listdir(full_folder_path)
        dict_meta_list = []
        for file in files_in_folder:
            with dcmread(f"{full_folder_path}\{file}") as dcm_file:
                dict_meta = dcm_file.to_json_dict()
                del dict_meta["7FE00010"]
            dict_meta_list.append(dict_meta)
        return dict_meta_list

    # def _extract_values_from_full_meta(self, full_meta: dict) -> dict:
    #     """Extracts truncated metadata from the full metadata dict
    #     HARDCODED!!!
    #     """
    #     # TODO:
    #     # add ContainerIdentifier, SpecimenDescription
    #     truncated_meta = {
    #         "Slozka vzorku": full_meta["0020000D"].get("Value", " ")[0],
    #         "Nazev vzorku": full_meta["00100020"].get("Value", " ")[0],
    #         "Jmeno pacienta": self._handle_structured_values(
    #             full_meta["00100010"].get("Value", " "), "Alphabetic"
    #         ),
    #         "Pohlavi pacienta": full_meta["00100040"].get("Value", " ")[0],
    #         "Datum narozeni pacienta": self._format_date(
    #             full_meta["00100030"].get("Value", " ")[0]
    #         ),
    #         "Datum odberu": self._format_date(
    #             full_meta["00080020"].get("Value", " ")[0]
    #         ),
    #     }
    #     return truncated_meta

    # def _handle_structured_values(self, value_attribute: list, desired_key: str) -> str:
    #     """Handles Values of a tag that contain a dictionary type"""
    #     if value_attribute == " ":
    #         return " "
    #     for item in value_attribute:
    #         if type(item) == dict:
    #             return item[desired_key]
    #         elif type(item) == dict:
    #             return " "

    # def format_date(self, date: str) -> str:
    #     """Formats date from yyyymmdd to yyyy-mm-dd"""
    #     return f"{date[:4]}-{date[4:6]}-{date[6:]}"

    def _translate_codes(self, full_dict: dict) -> dict:
        """Translates the DICOM codes to their respective strings"""
        all_keys = full_dict.keys()
        new_all_keys = []
        for key in all_keys:
            new_all_keys.append(dictionary_keyword(key))
            # check for nested dicts
            if (
                type(full_dict[key]) == dict
                and full_dict[key].get("vr") == "SQ"
                and not full_dict[key].get("Value") == []
            ):
                nested_dict = self._translate_codes(full_dict[key]["Value"][0])
                full_dict[key] = nested_dict
        return dict(zip(new_all_keys, full_dict.values()))

    def loop_through_instances(self, force_renew: bool = False) -> None:
        """Loops through folders in the DICOM images folder and performs metadata extraction"""

        folders = os.listdir(self.path_to_dicom_folders)
        folder_id = 1

        for folder in folders:
            try:
                full_meta = self._get_metadata(folder)
            except NotADirectoryError:
                continue
            logging.info(f"Zahajeno ukladani metadat ze slozky {folder}")
            for dictionary in full_meta:
                translated_dictionary = self._translate_codes(dictionary)

                self.write_to_database(
                    translated_dictionary, self.sql_string_SpecimenSession, folder_id
                )
                self.write_to_database(
                    translated_dictionary["SpecimenDescriptionSequence"],
                    self.sql_string_SpecimenDescriptionSequence,
                    folder_id,
                )
                self.write_to_database(
                    translated_dictionary["SpecimenDescriptionSequence"][
                        "PrimaryAnatomicStructureSequence"
                    ],
                    self.sql_string_PrimaryAnatomicStructureSequence,
                    folder_id,
                )
            folder_id += 1
        logging.info("Vsechna metadata jsou ulozena!")

    # def _check_for_changes(self) -> list:
    #     written_folders = pd.read_csv(self.path_to_truncdata_csv)["ID vzorku"].to_list()
    #     available_folders = os.listdir(self.path_to_dicom_folders)
    #     folder_difference = [
    #         folder for folder in available_folders if folder not in written_folders
    #     ]
    #     return folder_difference

    def write_to_database(
        self, meta_dict: dict, sql_string: str, folder_id: int
    ) -> None:
        """WIP function for writing into database"""
        database = sqlite3.connect(self.database_path)
        new_values = []
        for key, value in meta_dict.items():
            new_values.append(str(value.get("Value", "   "))[1:-1])
        meta_dict = dict(zip(meta_dict.keys(), new_values))
        meta_dict["FolderID"] = folder_id

        cursor = database.cursor()
        cursor.execute(
            sql_string,
            meta_dict,
        )
        database.commit()


# TESTING
metadata_ext = MetadataExtractor("extractor_app\config.ini")
metadata_ext.loop_through_instances()
