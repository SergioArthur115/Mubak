from functools import wraps
from flask import session, redirect, url_for
from models.user_model import get_user_by_id

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user = get_user_by_id(session['user_id'])

        if not user['is_admin']:
            return "Acesso negado"

        return f(*args, **kwargs)
    return decorated