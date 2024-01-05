from metadata_extractor import TerminalHandler


def main():
    configfile = "config.ini"
    handler = TerminalHandler(configfile)
    handler.handle_user()


if __name__ == "__main__":
    main()
