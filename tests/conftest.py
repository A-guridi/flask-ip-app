import os
import tempfile
import pytest
from ip_app import create_app
from ip_app.model import get_db, init_db


with open(os.path.join(os.path.dirname(__file__), 'fill_values.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    """
    Default fixture to create a testing app. This app uses the tempfile to create a temporary db that is deleted after all the tests pass.
    The function initializes the db and executes an SQL script to fill it with some values for users and blocked ips
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'dev'
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # after testing close the db connection
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
