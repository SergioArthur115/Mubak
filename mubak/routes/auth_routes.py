from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.usuario_model import criar_usuario, get_usuario_por_email
import os, uuid
from config import UPLOAD_FOLDER

bp = Blueprint('auth', __name__)


@bp.route('/check_email')
def check_email():
    email = request.args.get('email', '')
    user = get_usuario_por_email(email)
    return jsonify({'exists': bool(user)})


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        senha     = request.form.get('senha', '')
        telefone  = request.form.get('telefone', '').strip()
        cpf       = request.form.get('cpf', '').strip()
        data_nasc = request.form.get('data_nasc', '')
        file      = request.files.get('foto')

        if get_usuario_por_email(email):
            flash('E-mail já cadastrado.')
            return redirect(url_for('auth.register'))

        filename = 'default.png'
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        criar_usuario(
            nome, email, generate_password_hash(senha),
            telefone, cpf, data_nasc, filename
        )
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('auth.login'))

    return render_template('pages/cadastro.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        user  = get_usuario_por_email(email)

        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id_usuario']
            session['user_nome'] = user['nome']
            session['is_admin'] = (user['id_perfil'] == 1)

            if user['id_perfil'] == 1:
                return redirect(url_for('admin.painel'))
            return redirect(url_for('user.perfil'))

        flash('E-mail ou senha incorretos.')

    return render_template('pages/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
