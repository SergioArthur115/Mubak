from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.usuario_model import get_usuario_por_id, atualizar_usuario, criar_endereco, get_enderecos_usuario
from models.pedido_model import get_pedidos_usuario, get_itens_pedido
from utils.decorators import login_required
import os, uuid
from config import UPLOAD_FOLDER

bp = Blueprint('user', __name__)


@bp.route('/perfil')
@login_required
def perfil():
    user = get_usuario_por_id(session['user_id'])
    return render_template('pages/perfil.html', user=user)


@bp.route('/perfil/dados', methods=['GET', 'POST'])
@login_required
def perfil_dados():
    id_usuario = session['user_id']
    user = get_usuario_por_id(id_usuario)

    if request.method == 'POST':
        nome     = request.form.get('nome', '').strip()
        email    = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        file     = request.files.get('foto')

        filename = user['foto']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        atualizar_usuario(id_usuario, nome, email, telefone, filename)
        session['user_nome'] = nome
        flash('Dados atualizados com sucesso!')
        return redirect(url_for('user.perfil_dados'))

    return render_template('pages/perfil_dados.html', user=user)


@bp.route('/perfil/enderecos', methods=['GET', 'POST'])
@login_required
def perfil_enderecos():
    id_usuario = session['user_id']

    if request.method == 'POST':
        criar_endereco(
            id_usuario,
            cep         = request.form.get('cep', '').strip(),
            bairro      = request.form.get('bairro', '').strip(),
            cidade      = request.form.get('cidade', '').strip(),
            estado      = request.form.get('estado', '').strip(),
            complemento = request.form.get('complemento', '').strip(),
            numero      = request.form.get('numero', '').strip(),
            principal   = bool(request.form.get('principal'))
        )
        flash('Endereço adicionado!')
        return redirect(url_for('user.perfil_enderecos'))

    enderecos = get_enderecos_usuario(id_usuario)
    return render_template('pages/perfil_enderecos.html', enderecos=enderecos)


@bp.route('/perfil/pedidos')
@login_required
def perfil_pedidos():
    pedidos = get_pedidos_usuario(session['user_id'])
    return render_template('pages/perfil_pedidos.html', pedidos=pedidos)


@bp.route('/perfil/pedidos/<int:id_pedido>')
@login_required
def detalhe_pedido(id_pedido):
    itens = get_itens_pedido(id_pedido)
    return render_template('pages/detalhe_pedido.html', itens=itens, id_pedido=id_pedido)
