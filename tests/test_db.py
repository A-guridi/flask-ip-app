import sqlite3

import pytest
from ip_app.model import get_db


def test_get_close_db(app):
    # tests wether the db is really closed by running a simple query and fetching the error
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    # tests that the db is intialiazed with some monkey patching
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # we use Pytest's monkey patching to avoid calling the init_db command
    monkeypatch.setattr('ip_app.model.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called