import functools
from werkzeug.security import generate_password_hash
from flask import request
from ip_app.model import get_db
from http import HTTPStatus as HS


def require_api_key(func):
    """
    Function wraper to require a valid api-key to call a certain route.
    It will check wether the api-key is stored on the database and return a 403 error if no api-key is provided
    or is not valid
    """
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if request.json:
            api_key = request.headers.get("api_key")
        else:
            return {"message": "Please provide an API key"}, HS.FORBIDDEN
        # Check if API key is correct and valid
        if valid_api_key(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": f"The provided API key {api_key} is not valid"}, HS.FORBIDDEN
    return decorator


def valid_api_key(api_key:str) -> bool:
    # checks wether a hased api-key value is on the table (is a registered api-key or not)
    db = get_db()
    api_saved= db.execute('SELECT CASE WHEN EXISTS(SELECT * FROM users WHERE apikey = ?)'
                          'THEN 1 ELSE 0 END', (api_key,)).fetchone()
    return api_saved[0]==1