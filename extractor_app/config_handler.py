import configparser


class ConfigHandler:
    def __init__(self, config_path: str = "extractor_app/config.ini") -> None:
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def handle_config(self, section: str, *args) -> list:
        option_list = []
        for option in args:
            option_list.append(self.config[section][option])
        return option_list
