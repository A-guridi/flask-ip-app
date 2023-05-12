import sqlite3

import click
from flask import current_app, g


def get_db():
    # returns the current db to execute SQL commands
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    # closes the current db, returning None if it was closed already
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # initializes the current db, running a script to create 3 new tables
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    # wraper around init_db to call it from terminal by using the click decorator
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # function to start the db from the app constructor, deleting previous ones
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    