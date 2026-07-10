from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.carrinho_model import (
    get_carrinho_usuario, adicionar_ao_carrinho,
    atualizar_quantidade, remover_do_carrinho,
    limpar_carrinho, total_carrinho
)
from models.produto_model import get_produto_por_id
from models.usuario_model import get_enderecos_usuario
from models.pedido_model import criar_pedido, adicionar_item_pedido, registrar_pagamento
from models.cupom_model import validar_cupom
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


# ── Cupom de desconto ────────────────────────────────────────────────────────

@bp.route('/carrinho/cupom/aplicar', methods=['POST'])
@login_required
def aplicar_cupom():
    codigo = request.form.get('codigo_cupom', '').strip()
    cupom = validar_cupom(codigo)

    if not cupom:
        session.pop('cupom_aplicado', None)
        flash('Cupom inválido, expirado ou inativo.')
    else:
        session['cupom_aplicado'] = {
            'id_cupom': cupom['id_cupom'],
            'codigo': cupom['codigo'],
            'valor': cupom['valor']
        }
        flash(f'Cupom "{cupom["codigo"]}" aplicado com sucesso!')

    return redirect(url_for('carrinho.finalizar'))


@bp.route('/carrinho/cupom/remover')
@login_required
def remover_cupom():
    session.pop('cupom_aplicado', None)
    flash('Cupom removido.')
    return redirect(url_for('carrinho.finalizar'))


# ── Finalizar compra ─────────────────────────────────────────────────────────

@bp.route('/carrinho/finalizar', methods=['GET', 'POST'])
@login_required
def finalizar():
    id_usuario = session['user_id']
    itens = get_carrinho_usuario(id_usuario)

    if not itens:
        flash('Seu carrinho está vazio.')
        return redirect(url_for('carrinho.carrinho'))

    enderecos = get_enderecos_usuario(id_usuario)
    subtotal = total_carrinho(id_usuario)

    # Revalida o cupom guardado na sessão a cada acesso (pode ter expirado
    # ou sido desativado pelo admin entre a aplicação e a finalização).
    cupom_sessao = session.get('cupom_aplicado')
    desconto = 0
    if cupom_sessao:
        cupom_atual = validar_cupom(cupom_sessao['codigo'])
        if cupom_atual:
            desconto = round(subtotal * (cupom_atual['valor'] / 100), 2)
            desconto = min(desconto, subtotal)
        else:
            session.pop('cupom_aplicado', None)
            cupom_sessao = None

    total = round(subtotal - desconto, 2)

    if request.method == 'POST':
        id_endereco = request.form.get('id_endereco')
        metodo      = request.form.get('metodo_pagamento', 'cartao')

        if not id_endereco:
            flash('Selecione um endereço de entrega.')
            return redirect(url_for('carrinho.finalizar'))

        id_cupom_aplicado = cupom_sessao['id_cupom'] if cupom_sessao else None

        id_pedido = criar_pedido(
            id_usuario, int(id_endereco), total,
            id_cupom=id_cupom_aplicado, valor_desconto=desconto
        )

        for item in itens:
            adicionar_item_pedido(
                id_pedido, item['id_produto'],
                item['quantidade'], item['preco_unitario']
            )

        registrar_pagamento(id_pedido, metodo, total)
        limpar_carrinho(id_usuario)
        session.pop('cupom_aplicado', None)
        flash(f'Pedido #{id_pedido} realizado com sucesso!')
        return redirect(url_for('user.perfil_pedidos'))

    return render_template(
        'pages/finalizar.html',
        itens=itens, subtotal=subtotal, desconto=desconto, total=total,
        enderecos=enderecos, cupom_aplicado=cupom_sessao
    )
