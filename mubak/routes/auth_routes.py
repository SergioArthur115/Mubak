from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, get_user_by_email
import os
from config import UPLOAD_FOLDER

bp = Blueprint('auth', __name__)

@bp.route('/check_email')
def check_email():
    email = request.args.get('email')
    user = get_user_by_email(email)
    return jsonify({'exists': bool(user)})

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        file = request.files.get('foto')

        if get_user_by_email(email):
            flash('Email já cadastrado')
            return redirect(url_for('auth.register'))

        filename = 'default.png'
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        create_user(nome,email,generate_password_hash(senha),filename)
        flash('Cadastro realizado')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_email(request.form.get('email'))

        if user and check_password_hash(user['senha'], request.form.get('senha')):
            session['user_id'] = user['id']

            if user['is_admin']:
                return redirect(url_for('admin.admin'))

            return redirect(url_for('user.perfil'))

        flash('Login inválido')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))