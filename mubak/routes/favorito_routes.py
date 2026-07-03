from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.favorito_model import get_favoritos_usuario, toggle_favorito, remover_favorito
from models.produto_model import get_produto_por_id
from utils.decorators import login_required

bp = Blueprint('favorito', __name__)


@bp.route('/favoritos')
@login_required
def favoritos():
    itens = get_favoritos_usuario(session['user_id'])
    return render_template('pages/favoritos.html', itens=itens)


@bp.route('/favoritos/toggle/<int:id_produto>', methods=['POST'])
@login_required
def toggle(id_produto):
    prod = get_produto_por_id(id_produto)
    if not prod:
        flash('Produto não encontrado.')
        return redirect(url_for('produto.produtos'))

    adicionado = toggle_favorito(session['user_id'], id_produto)
    if adicionado:
        flash(f'"{prod["nome"]}" adicionado aos favoritos!')
    else:
        flash(f'"{prod["nome"]}" removido dos favoritos.')

    # Sempre que possível volta para a mesma página em que o usuário estava.
    destino = request.form.get('proximo')
    if destino:
        return redirect(destino)
    return redirect(url_for('produto.produto', id_produto=id_produto))


@bp.route('/favoritos/remover/<int:id_produto>')
@login_required
def remover(id_produto):
    remover_favorito(session['user_id'], id_produto)
    flash('Produto removido dos favoritos.')
    return redirect(url_for('favorito.favoritos'))
