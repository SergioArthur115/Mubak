from flask import Blueprint, render_template, request, redirect, url_for, session  # flask
from models.user_model import get_all_users, get_user_by_id, update_user, delete_user  # model
from utils.decorators import admin_required  # proteção
import os  # arquivos
import uuid  # gerar nome único
from config import UPLOAD_FOLDER  # pasta upload

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@admin_required
def admin():
    search = request.args.get('search','').lower()  # busca
    order = request.args.get('order','nome')  # ordenação
    page = int(request.args.get('page',1))  # página atual

    per_page = 5  # usuários por página

    users = get_all_users()  # lista todos

    # FILTRO (nome OU email)
    if search:
        users = [
            u for u in users
            if search in u['nome'].lower() or search in u['email'].lower()
        ]

    # ORDENAÇÃO
    users = sorted(users, key=lambda x: x[order])

    # PAGINAÇÃO
    total = len(users)
    start = (page - 1) * per_page
    end = start + per_page
    users_paginated = users[start:end]

    total_pages = (total // per_page) + (1 if total % per_page else 0)

    return render_template(
        'admin.html',
        users=users_paginated,
        page=page,
        total_pages=total_pages,
        search=search,
        order=order
    )

# EDITAR
@bp.route('/admin/edit/<int:id>', methods=['GET','POST'])
@admin_required
def edit(id):
    user = get_user_by_id(id)

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        file = request.files.get('foto')

        filename = user['foto']

        # nome único para imagem
        if file and file.filename != '':
            ext = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        update_user(id, nome, email, filename)

        return redirect(url_for('admin.admin'))

    return render_template('edit_user.html', user=user)

# EXCLUIR
@bp.route('/admin/delete/<int:id>')
@admin_required
def delete(id):
    # impede excluir a si mesmo
    if session['user_id'] == id:
        return "Você não pode excluir a si mesmo"

    delete_user(id)
    return redirect(url_for('admin.admin'))