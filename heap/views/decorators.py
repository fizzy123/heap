from functools import wraps
from flask import session, redirect, url_for, jsonify

def login_required_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('ui.signin_view'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return jsonify({'url': url_for('ui.signin_view')})
        return f(*args, **kwargs)
    return decorated_function
