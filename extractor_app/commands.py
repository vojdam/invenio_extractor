import click

from . import metadata_extractor
from . import db


@click.command("update-db")
@click.option("-r", "--renew", is_flag=True, help="Re-extract all folders.")
def update_database(renew: bool = False) -> None:
    """Updates the database"""
    me = metadata_extractor.MetadataExtractor()
    me.loop_through_instances(force_renew=renew)


@click.command("init-db")
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    db.init_db()
    click.echo("Initialized the database.")
