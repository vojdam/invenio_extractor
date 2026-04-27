import configparser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigHandler:
    def __init__(self, config_path: str = "config.ini") -> None:
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def resolve_project_path(self, path_value: str) -> Path:
        path = Path(path_value).expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()

    def handle_config(self, section: str, *args) -> list:
        option_list = []
        for option in args:
            option_list.append(self.config[section][option])
        return option_list
