from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.carrinho_model import (
    get_carrinho_usuario, adicionar_ao_carrinho,
    atualizar_quantidade, remover_do_carrinho,
    limpar_carrinho, total_carrinho
)
from models.produto_model import get_produto_por_id
from models.usuario_model import get_enderecos_usuario
from models.pedido_model import criar_pedido, adicionar_item_pedido, registrar_pagamento
from utils.decorators import login_required

bp = Blueprint('carrinho', __name__)


@bp.route('/carrinho')
@login_required
def carrinho():
    itens = get_carrinho_usuario(session['user_id'])
    total = total_carrinho(session['user_id'])
    return render_template('pages/carrinho.html', itens=itens, total=total)


@bp.route('/carrinho/adicionar/<int:id_produto>', methods=['POST'])
@login_required
def adicionar(id_produto):
    prod = get_produto_por_id(id_produto)
    if not prod:
        flash('Produto não encontrado.')
        return redirect(url_for('produto.produtos'))

    quantidade = int(request.form.get('quantidade', 1))
    adicionar_ao_carrinho(session['user_id'], id_produto, quantidade, prod['preco'])
    flash(f'"{prod["nome"]}" adicionado ao carrinho!')
    return redirect(url_for('produto.produto', id_produto=id_produto))


@bp.route('/carrinho/atualizar/<int:id_produto>', methods=['POST'])
@login_required
def atualizar(id_produto):
    quantidade = int(request.form.get('quantidade', 1))
    atualizar_quantidade(session['user_id'], id_produto, quantidade)
    return redirect(url_for('carrinho.carrinho'))


@bp.route('/carrinho/remover/<int:id_produto>')
@login_required
def remover(id_produto):
    remover_do_carrinho(session['user_id'], id_produto)
    return redirect(url_for('carrinho.carrinho'))


@bp.route('/carrinho/finalizar', methods=['GET', 'POST'])
@login_required
def finalizar():
    id_usuario = session['user_id']
    itens = get_carrinho_usuario(id_usuario)

    if not itens:
        flash('Seu carrinho está vazio.')
        return redirect(url_for('carrinho.carrinho'))

    enderecos = get_enderecos_usuario(id_usuario)

    if request.method == 'POST':
        id_endereco = request.form.get('id_endereco')
        metodo      = request.form.get('metodo_pagamento', 'cartao')

        if not id_endereco:
            flash('Selecione um endereço de entrega.')
            return redirect(url_for('carrinho.finalizar'))

        valor_total = total_carrinho(id_usuario)
        id_pedido   = criar_pedido(id_usuario, int(id_endereco), valor_total)

        for item in itens:
            adicionar_item_pedido(
                id_pedido, item['id_produto'],
                item['quantidade'], item['preco_unitario']
            )

        registrar_pagamento(id_pedido, metodo, valor_total)
        limpar_carrinho(id_usuario)
        flash(f'Pedido #{id_pedido} realizado com sucesso!')
        return redirect(url_for('user.perfil_pedidos'))

    total = total_carrinho(id_usuario)
    return render_template(
        'pages/finalizar.html',
        itens=itens, total=total, enderecos=enderecos
    )
