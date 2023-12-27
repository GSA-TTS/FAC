import logging
import boto3
import os
import click
from peewee import Model, SqliteDatabase, TextField, BooleanField
from types import SimpleNamespace
from commands.constants import *
from commands import (
    setup, 
    load, 
    prep, 
    check
    )

logger = logging.getLogger(__name__)

def zero_pad(n):
    if n < 10:
        return f"0{n}"
    else:
        return "f{n}"

@click.group()
def cli():
    pass

if __name__ == '__main__':
    cli.add_command(setup.setup)
    cli.add_command(load.load)
    cli.add_command(prep.prep)
    cli.add_command(check.check)
    cli()