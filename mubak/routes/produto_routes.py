from flask import Blueprint, render_template, request
from models.produto_model import (
    get_todos_produtos, get_produto_por_id,
    get_imagens_produto, get_todas_categorias, get_produtos_destaque
)

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

    return render_template(
        'pages/produtos.html',
        produtos=lista,
        categorias=categorias,
        categoria_ativa=categoria,
        busca=busca or ''
    )


@bp.route('/produto/<int:id_produto>')
def produto(id_produto):
    prod = get_produto_por_id(id_produto)
    if not prod:
        return "Produto não encontrado", 404

    imagens = get_imagens_produto(id_produto)
    return render_template('pages/produto.html', produto=prod, imagens=imagens)


@bp.route('/pesquisar')
def pesquisar():
    busca = request.args.get('q', '').strip()
    lista = get_todos_produtos(busca=busca) if busca else []
    categorias = get_todas_categorias()
    return render_template(
        'pages/produtos.html',
        produtos=lista,
        categorias=categorias,
        categoria_ativa=None,
        busca=busca
    )
