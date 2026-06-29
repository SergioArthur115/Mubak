from flask import Blueprint, render_template, request, session
from models.user_model import get_user_by_id, update_user
from utils.decorators import login_required
import os
import uuid  # gerar nome único
from config import UPLOAD_FOLDER

bp = Blueprint('user', __name__)

@bp.route('/perfil', methods=['GET','POST'])
@login_required
def perfil():
    user_id = session['user_id']

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        file = request.files.get('foto')

        user = get_user_by_id(user_id)

        filename = user['foto']

        # nome único imagem
        if file and file.filename != '':
            ext = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        update_user(user_id, nome, email, filename)

    user = get_user_by_id(user_id)
    return render_template('perfil.html', user=user)