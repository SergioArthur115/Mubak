from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models.usuario_model import (
    get_todos_usuarios, get_usuario_por_id, atualizar_usuario, deletar_usuario,
    buscar_usuarios, get_usuario_por_email, criar_usuario, atualizar_usuario_admin
)
from models.produto_model import (
    get_todos_produtos, get_produto_por_id, criar_produto,
    atualizar_produto, deletar_produto, adicionar_imagem_produto, get_todas_categorias
)
from utils.decorators import admin_required
import os, uuid
from config import UPLOAD_FOLDER

bp = Blueprint('admin', __name__)


# ── Painel ─────────────────────────────────────────────────────────────────────

@bp.route('/admin')
@admin_required
def painel():
    # Consulta administrativa: o admin pode buscar usuários por nome e/ou e-mail.
    busca_nome  = request.args.get('busca_nome', '').strip()
    busca_email = request.args.get('busca_email', '').strip()
    search = request.args.get('search', '').lower()  # mantém compatibilidade com busca simples antiga
    order  = request.args.get('order', 'nome')
    page   = int(request.args.get('page', 1))
    per_page = 10

    if busca_nome or busca_email:
        users = buscar_usuarios(nome=busca_nome or None, email=busca_email or None)
    else:
        users = get_todos_usuarios()
        if search:
            users = [u for u in users if search in u['nome'].lower() or search in u['email'].lower()]

    validos = ['nome', 'email', 'id_usuario']
    order = order if order in validos else 'nome'
    users = sorted(users, key=lambda x: x[order])

    total       = len(users)
    start       = (page - 1) * per_page
    users_page  = users[start:start + per_page]
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        'pages/admin.html',
        users=users_page,
        page=page,
        total_pages=total_pages,
        search=search,
        busca_nome=busca_nome,
        busca_email=busca_email,
        order=order
    )


# ── Usuários ───────────────────────────────────────────────────────────────────

@bp.route('/admin/usuario/novo', methods=['GET', 'POST'])
@admin_required
def novo_usuario():
    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        senha     = request.form.get('senha', '')
        telefone  = request.form.get('telefone', '').strip()
        cpf       = request.form.get('cpf', '').strip()
        data_nasc = request.form.get('data_nasc', '')
        id_perfil = int(request.form.get('id_perfil', 2))
        file      = request.files.get('foto')

        if get_usuario_por_email(email):
            flash('E-mail já cadastrado.')
            return redirect(url_for('admin.novo_usuario'))

        filename = 'default.png'
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        criar_usuario(
            nome, email, generate_password_hash(senha),
            telefone, cpf, data_nasc, filename, id_perfil
        )
        flash('Usuário criado com sucesso!')
        return redirect(url_for('admin.painel'))

    return render_template('pages/admin_usuario_form.html', user=None)


@bp.route('/admin/usuario/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    user = get_usuario_por_id(id)
    if not user:
        return "Usuário não encontrado", 404

    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        telefone  = request.form.get('telefone', '').strip()
        id_perfil = int(request.form.get('id_perfil', user['id_perfil']))
        file      = request.files.get('foto')

        filename = user['foto']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        atualizar_usuario_admin(id, nome, email, telefone, filename, id_perfil)
        flash('Usuário atualizado.')
        return redirect(url_for('admin.painel'))

    return render_template('pages/admin_usuario_form.html', user=user)


@bp.route('/admin/usuario/deletar/<int:id>')
@admin_required
def deletar_usuario_view(id):
    # Regra de negócio: o admin não pode excluir a si mesmo.
    if session['user_id'] == id:
        flash('Você não pode excluir a si mesmo.')
        return redirect(url_for('admin.painel'))
    deletar_usuario(id)
    flash('Usuário excluído.')
    return redirect(url_for('admin.painel'))


# ── Produtos ───────────────────────────────────────────────────────────────────

@bp.route('/admin/produtos')
@admin_required
def admin_produtos():
    busca     = request.args.get('q', '')
    categoria = request.args.get('categoria')
    produtos  = get_todos_produtos(categoria_nome=categoria, busca=busca)
    categorias = get_todas_categorias()
    return render_template(
        'pages/admin_produtos.html',
        produtos=produtos,
        categorias=categorias,
        busca=busca,
        categoria_ativa=categoria
    )


@bp.route('/admin/produto/novo', methods=['GET', 'POST'])
@admin_required
def novo_produto():
    categorias = get_todas_categorias()

    if request.method == 'POST':
        nome                 = request.form.get('nome', '').strip()
        descricao            = request.form.get('descricao', '').strip()
        especificacao_tecnica = request.form.get('especificacao_tecnica', '').strip()
        preco                = float(request.form.get('preco', 0))
        estoque              = int(request.form.get('estoque', 0))
        id_categoria         = int(request.form.get('id_categoria', 0))
        status_prod          = request.form.get('status_prod', 'ativo')
        files                = request.files.getlist('imagens')

        id_novo = criar_produto(
            nome, descricao, especificacao_tecnica,
            preco, estoque, id_categoria, status_prod
        )

        for file in files:
            if file and file.filename:
                ext      = file.filename.rsplit('.', 1)[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                adicionar_imagem_produto(id_novo, filename)

        flash('Produto criado com sucesso!')
        return redirect(url_for('admin.admin_produtos'))

    return render_template('pages/admin_produto_form.html', produto=None, categorias=categorias)


@bp.route('/admin/produto/editar/<int:id_produto>', methods=['GET', 'POST'])
@admin_required
def editar_produto(id_produto):
    prod       = get_produto_por_id(id_produto)
    categorias = get_todas_categorias()

    if not prod:
        return "Produto não encontrado", 404

    if request.method == 'POST':
        nome                 = request.form.get('nome', '').strip()
        descricao            = request.form.get('descricao', '').strip()
        especificacao_tecnica = request.form.get('especificacao_tecnica', '').strip()
        preco                = float(request.form.get('preco', 0))
        estoque              = int(request.form.get('estoque', 0))
        id_categoria         = int(request.form.get('id_categoria', 0))
        status_prod          = request.form.get('status_prod', 'ativo')
        files                = request.files.getlist('imagens')

        atualizar_produto(
            id_produto, nome, descricao, especificacao_tecnica,
            preco, estoque, id_categoria, status_prod
        )

        for file in files:
            if file and file.filename:
                ext      = file.filename.rsplit('.', 1)[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                adicionar_imagem_produto(id_produto, filename)

        flash('Produto atualizado!')
        return redirect(url_for('admin.admin_produtos'))

    return render_template('pages/admin_produto_form.html', produto=prod, categorias=categorias)


@bp.route('/admin/produto/deletar/<int:id_produto>')
@admin_required
def deletar_produto_view(id_produto):
    deletar_produto(id_produto)
    flash('Produto excluído.')
    return redirect(url_for('admin.admin_produtos'))
