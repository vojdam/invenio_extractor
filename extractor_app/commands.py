import click

from . import metadata_extractor
from . import db


@click.command("update-db")
def update_database():
    """Updates the database"""
    me = metadata_extractor.MetadataExtractor()
    me.loop_through_instances()


@click.command("init-db")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    db.init_db()
    click.echo("Initialized the database.")
