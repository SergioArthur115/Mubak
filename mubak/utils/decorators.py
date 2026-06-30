from functools import wraps
from flask import session, redirect, url_for
from models.usuario_model import get_usuario_por_id


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
        user = get_usuario_por_id(session['user_id'])
        if not user or user['id_perfil'] != 1:
            return "Acesso negado", 403
        return f(*args, **kwargs)
    return decorated
