from flask import Flask, render_template, session, redirect, url_for
from datetime import timedelta, datetime
from database import init_db
from routes.auth_routes import bp as auth_bp
from routes.user_routes import bp as user_bp
from routes.admin_routes import bp as admin_bp
from routes.produto_routes import bp as produto_bp
from routes.carrinho_routes import bp as carrinho_bp
from routes.favorito_routes import bp as favorito_bp
from models.produto_model import get_produtos_destaque
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Tempo máximo de inatividade permitido antes do logout automático.
TEMPO_INATIVIDADE = timedelta(minutes=5)
app.permanent_session_lifetime = TEMPO_INATIVIDADE

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(carrinho_bp)
app.register_blueprint(favorito_bp)


@app.before_request
def verificar_inatividade():
    """
    Desloga o usuário automaticamente após 5 minutos sem nenhuma
    requisição (navegação, atualização de página, ações no sistema).
    """
    if 'user_id' in session:
        agora = datetime.now()
        ultima_atividade = session.get('ultima_atividade')

        if ultima_atividade:
            ultima_atividade = datetime.fromisoformat(ultima_atividade)
            if agora - ultima_atividade > TEMPO_INATIVIDADE:
                session.clear()
                return redirect(url_for('auth.login'))

        session.permanent = True
        session['ultima_atividade'] = agora.isoformat()


@app.route('/')
def index():
    destaques = get_produtos_destaque(limite=8)
    return render_template('index.html', destaques=destaques)


if __name__ == '__main__':
    app.run(debug=True)
