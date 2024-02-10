import sqlite3

from . import config_handler

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def check_for_new_custom_columns(cursor, new_data: str) -> str:
    current_data = cursor.execute("select * from CustomData")
    current_columns = list(map(lambda x: x[0], current_data.description))[2:]
    if len(new_data) > len(current_columns):
        new_columns = list(set(new_data) - set(current_columns))
        for col in new_columns:
            cursor.execute(f"ALTER TABLE CustomData ADD COLUMN '{col}' 'TEXT'")


def create_custom_data_table() -> None:
    cf_handler = config_handler.ConfigHandler()
    custom_data = cf_handler.handle_config("VARS", "CustomData")[0]
    custom_data = custom_data.split(", ")

    db = get_db()
    cur = db.cursor()

    if custom_data is not None:
        check_for_new_custom_columns(cur, custom_data)
        custom_data = " TEXT, ".join(custom_data) + " TEXT, "
        cur.execute(
            f"""CREATE TABLE IF NOT EXISTS CustomData (
                    CustomDataID INTEGER PRIMARY KEY,
                    FolderID INTEGER,
                    {custom_data}
                    FOREIGN KEY (FolderID) REFERENCES SpecimenSession(FolderID),
                    FOREIGN KEY (CustomDataID) REFERENCES SpecimenSession(SpecimenSessionID)
        )"""
        )
        db.commit()


def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
