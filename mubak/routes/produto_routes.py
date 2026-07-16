from flask import Blueprint, render_template, request, session, Response, url_for, redirect
from models.produto_model import (
    get_todos_produtos, get_produto_por_id,
    get_imagens_produto, get_todas_categorias, get_produtos_destaque,
    get_imagem_por_id
)
from models.favorito_model import get_ids_favoritos_usuario, is_favorito

bp = Blueprint('produto', __name__)


@bp.route('/produtos')
def produtos():
    categoria = request.args.get('categoria')
    preco_min = request.args.get('preco_min')
    preco_max = request.args.get('preco_max')
    busca     = request.args.get('q')

    lista = get_todos_produtos(
        categoria_nome=categoria,
        preco_min=preco_min,
        preco_max=preco_max,
        busca=busca
    )
    categorias = get_todas_categorias()

    favoritos_ids = set()
    if session.get('user_id'):
        favoritos_ids = get_ids_favoritos_usuario(session['user_id'])

    return render_template(
        'pages/produtos.html',
        produtos=lista,
        categorias=categorias,
        categoria_ativa=categoria,
        busca=busca or '',
        favoritos_ids=favoritos_ids
    )


@bp.route('/produto/<int:id_produto>')
def produto(id_produto):
    prod = get_produto_por_id(id_produto)
    if not prod:
        return "Produto não encontrado", 404

    imagens = get_imagens_produto(id_produto)

    favoritado = False
    if session.get('user_id'):
        favoritado = is_favorito(session['user_id'], id_produto)

    return render_template(
        'pages/produto.html',
        produto=prod, imagens=imagens, favoritado=favoritado
    )


@bp.route('/pesquisar')
def pesquisar():
    busca = request.args.get('q', '').strip()
    lista = get_todos_produtos(busca=busca) if busca else []
    categorias = get_todas_categorias()

    favoritos_ids = set()
    if session.get('user_id'):
        favoritos_ids = get_ids_favoritos_usuario(session['user_id'])

    return render_template(
        'pages/produtos.html',
        produtos=lista,
        categorias=categorias,
        categoria_ativa=None,
        busca=busca,
        favoritos_ids=favoritos_ids
    )


@bp.route('/imagem_produto/<int:id_imagem>')
def imagem_produto(id_imagem):
    """Serve a imagem de um produto diretamente do banco de dados (BLOB)."""
    img = get_imagem_por_id(id_imagem)
    if not img or not img['dados']:
        return redirect(url_for('static', filename='images/temp.png'))
    return Response(
        img['dados'],
        mimetype=img['mimetype'] or 'image/jpeg',
        headers={'Cache-Control': 'public, max-age=86400'}
    )
