from flask import Flask, render_template
from database import init_db
from routes.auth_routes import bp as auth_bp
from routes.user_routes import bp as user_bp
from routes.admin_routes import bp as admin_bp
from routes.produto_routes import bp as produto_bp
from routes.carrinho_routes import bp as carrinho_bp
from models.produto_model import get_produtos_destaque
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(carrinho_bp)


@app.route('/')
def index():
    destaques = get_produtos_destaque(limite=8)
    return render_template('index.html', destaques=destaques)


if __name__ == '__main__':
    app.run(debug=True)
