import functools
from werkzeug.security import generate_password_hash
from flask import request
from ip_app.model import get_db


def require_api_key(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if request.json:
            api_key = request.headers.get("api_key")
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if valid_api_key(generate_password_hash(api_key)):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator


def valid_api_key(hashed_key:str):
    # checks wether a hased api-key value is on the table (is a registered api-key or not)
    db = get_db()
    api_saved= db.execute('SELECT EXISTS(SELECT 1 FROM users WHERE apikey = ? LIMIT 1', ( hashed_key,)).fetchone()
    return api_saved[0]==1