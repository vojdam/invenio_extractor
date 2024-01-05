from pydicom import dcmread
from pydicom.datadict import dictionary_keyword
import os
import logging
import csv
import pandas as pd
import configparser


class MetadataExtractor:
    def __init__(
        self,
        path_to_dicom_folders: str,
        path_to_rawdata_csv: str,
        path_to_truncdata_csv: str,
    ) -> None:
        self.path_to_dicom_folders = path_to_dicom_folders
        self.path_to_rawdata_csv = path_to_rawdata_csv
        self.path_to_truncdata_csv = path_to_truncdata_csv
        self.values_to_extract = {
            "Slozka vzorku": None,
            "Nazev vzorku": None,
            "Jmeno pacienta": None,
            "Pohlavi pacienta": None,
            "Datum narozeni pacienta": None,
            "Datum odberu": None,
        }
        logging.basicConfig(level=logging.INFO)

    def _get_metadata(self, folder_path: str) -> dict:
        """Saves metadata from the DCM file to a dict"""
        full_folder_path = f"{self.path_to_dicom_folders}\{folder_path}"
        files_in_folder = os.listdir(full_folder_path)

        with dcmread(f"{full_folder_path}\{files_in_folder[0]}") as dcm_file:
            dict_meta = dcm_file.to_json_dict()
            del dict_meta["7FE00010"]
        return dict_meta

    # def save_to_json(self, meta: dict) -> None:
    #     """Saves full metadata to a JSON file"""
    #     with open(self.path_to_json, "a") as file:
    #         file.write(json.dumps(meta))
    #     logging.info(f"Metadata uspesne ulozena do JSON souboru: {self.path_to_json}")

    def save_to_csv(self, data: dict, path: str) -> None:
        """Saves data to a CSV file"""
        with open(path, "a") as file:
            append = csv.DictWriter(file, data.keys())
            append.writerow(data)
        logging.info(f"Metadata uspesne ulozena do CSV souboru: {path}")

    def _extract_values_from_full_meta(self, full_meta: dict) -> dict:
        """Extracts truncated metadata from the full metadata dict
        HARDCODED!!!
        """
        # TODO:
        # add ContainerIdentifier, SpecimenDescription
        truncated_meta = {
            "Slozka vzorku": full_meta["0020000D"].get("Value", " ")[0],
            "Nazev vzorku": full_meta["00100020"].get("Value", " ")[0],
            "Jmeno pacienta": self._handle_structured_values(
                full_meta["00100010"].get("Value", " "), "Alphabetic"
            ),
            "Pohlavi pacienta": full_meta["00100040"].get("Value", " ")[0],
            "Datum narozeni pacienta": self._format_date(
                full_meta["00100030"].get("Value", " ")[0]
            ),
            "Datum odberu": self._format_date(
                full_meta["00080020"].get("Value", " ")[0]
            ),
        }
        return truncated_meta

    def _handle_structured_values(self, value_attribute: list, desired_key: str) -> str:
        """Handles Values of a tag that contain a dictionary type"""
        if value_attribute == " ":
            return " "
        for item in value_attribute:
            if type(item) == dict:
                return item[desired_key]
            elif type(item) == dict:
                return " "

    def _format_date(self, date: str) -> str:
        """Formats date from yyyymmdd to yyyy-mm-dd"""
        return f"{date[:4]}-{date[4:6]}-{date[6:]}"

    def _init_truncdata_csv(self) -> None:
        """Initializes the CSV file for truncated metadata"""
        with open(self.path_to_truncdata_csv, "w") as file:
            write = csv.DictWriter(file, self.values_to_extract.keys())
            write.writeheader()
        logging.info("CSV soubor pro zkracena metadata inicializovan")

    def _init_rawdata_csv(self, data: dict) -> None:
        """Initializes the CSV file for raw metadata"""
        with open(self.path_to_rawdata_csv, "w") as file:
            write = csv.DictWriter(file, data.keys())
            write.writeheader()
        logging.info("CSV soubor pro raw metadata inicializovan")

    def _translate_codes(self, full_dict: dict) -> dict:
        """Translates the DICOM codes to their respective strings"""
        all_keys = full_dict.keys()
        new_all_keys = []
        for key in all_keys:
            new_all_keys.append(dictionary_keyword(key))
        return dict(zip(new_all_keys, full_dict.values()))

    def loop_through_instances(
        self, force_renew: bool = False, use_tags: bool = True
    ) -> None:
        """Loops through folders in the DICOM images folder and performs metadata extraction"""
        if not os.path.exists(self.path_to_truncdata_csv):
            self._init_truncdata_csv()

        if (
            force_renew
            and os.path.exists(self.path_to_rawdata_csv)
            and os.path.exists(self.path_to_truncdata_csv)
        ):
            folders = os.listdir(self.path_to_dicom_folders)
            os.remove(self.path_to_truncdata_csv)
            os.remove(self.path_to_rawdata_csv)
            self._init_truncdata_csv()
        elif (
            force_renew
            and not os.path.exists(self.path_to_rawdata_csv)
            and not os.path.exists(self.path_to_truncdata_csv)
        ):
            folders = os.listdir(self.path_to_dicom_folders)
        else:
            folders = self._check_for_changes()

        for folder in folders:
            try:
                full_meta = self._get_metadata(folder)
            except NotADirectoryError:
                continue
            logging.info(f"Zahajeno ukladani metadat ze slozky {folder}")
            full_meta_duplicate = full_meta
            if not use_tags:
                translated_full_meta = self._translate_codes(full_meta)
                full_meta = translated_full_meta
            # if not os.path.exists(self.path_to_truncdata_csv):
            #     self._init_truncdata_csv()
            if not os.path.exists(self.path_to_rawdata_csv):
                self._init_rawdata_csv(full_meta)
            self.save_to_csv(
                full_meta,
                self.path_to_rawdata_csv,
            )
            truncated_meta = self._extract_values_from_full_meta(full_meta_duplicate)
            self.save_to_csv(truncated_meta, self.path_to_truncdata_csv)
        logging.info("Vsechna metadata jsou ulozena!")

    def _check_for_changes(self) -> list:
        written_folders = pd.read_csv(self.path_to_truncdata_csv)["ID vzorku"].to_list()
        available_folders = os.listdir(self.path_to_dicom_folders)
        folder_difference = [
            folder for folder in available_folders if folder not in written_folders
        ]
        return folder_difference


class TerminalHandler:
    def __init__(self, path_to_config: str) -> None:
        self.running = True
        self.path_to_config = path_to_config
        self.config = configparser.ConfigParser()
        self.config.read(self.path_to_config)
        (
            self.path_to_trunc_data,
            self.path_to_raw_data,
            self.path_to_images,
            self.use_tags,
        ) = self.read_config()
        self.extractor = MetadataExtractor(
            self.path_to_images, self.path_to_raw_data, self.path_to_trunc_data
        )

    def read_config(self) -> list:
        """Reads paths from config"""
        return [
            self.config["PATHS"]["PathToTruncatedDataCSV"],
            self.config["PATHS"]["PathToRawDataCSV"],
            self.config["PATHS"]["PathToImagesFolder"],
            self.config.getboolean("OTHER", "UseDICOMTags"),
        ]

    # def set_config(
    #     self, section_to_set: str, key_to_set: str, value_to_set: str
    # ) -> None:
    #     """Sets config values"""
    #     self.config[section_to_set][key_to_set] = value_to_set
    #     with open(self.path_to_config, "w") as configfile:
    #         self.config.write(configfile)

    def handle_user(self):
        """Handles user interactions"""
        while True:
            input1 = input("Vyberte akci:\n1 ulozit metadata\n2 premazat metadata\n")
            match input1:
                case "1":
                    self.extractor.loop_through_instances(use_tags=self.use_tags)
                    break
                case "2":
                    self.extractor.loop_through_instances(
                        force_renew=True, use_tags=self.use_tags
                    )
                    break
                case _:
                    logging.warning("Neplatny znak")


# ext = MetadataExtractor(FOLDER_PATH, RAWCSV, "csv.csv")
# ext.loop_through_instances()

# handle = TerminalHandler("config.ini")
# handle.handle_user()
