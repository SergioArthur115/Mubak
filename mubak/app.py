from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Página inicial
@app.route("/")
def index():
    return render_template("index.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        senha = request.form.get("senha")
        # aqui você valida com o banco de dados futuramente
        if login == "admin" and senha == "1234":
            return redirect(url_for("index"))
        return render_template("pages/login.html", erro="Login ou senha incorretos")
    return render_template("pages/login.html")


# Cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        # salvar no banco futuramente
        return redirect(url_for("login"))
    return render_template("pages/cadastro.html")


# Produtos
@app.route("/produtos")
def produtos():
    # Captura os filtros da URL
    categoria_selecionada = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")

    # Exemplo de lista de produtos (futuramente virá do Banco de Dados)
    lista_produtos = [
        {"id": 1, "nome": "Placa de Vídeo RTX", "preco": 2500, "categoria": "Peças"},
        {"id": 2, "nome": "Laptops Gamer", "preco": 5000, "categoria": "Laptops"},
        {"id": 3, "nome": "Monitor 4K", "preco": 1200, "categoria": "Monitores"},
    ]

    # Lógica de filtragem simples
    if categoria_selecionada:
        lista_produtos = [
            p for p in lista_produtos if p["categoria"] == categoria_selecionada
        ]

    # Aqui poderias adicionar filtros de preço também

    return render_template(
        "pages/produtos.html",
        produtos=lista_produtos,
        categoria_ativa=categoria_selecionada,
    )


# Simulação de banco de dados
PRODUTOS = {
    1: {
        "nome": "Placa de Vídeo RTX",
        "preco": "2.500,00",
        "img": "temp.png",
        "desc": "Alta performance para jogos.",
    },
    2: {
        "nome": "Processador i9",
        "preco": "3.200,00",
        "img": "temp.png",
        "desc": "O mais rápido da categoria.",
    },
    # Adicione os outros aqui...
}


@app.route("/produto/<int:id>")
def produto(id):
    # Busca o produto pelo ID no nosso dicionário
    produto_encontrado = PRODUTOS.get(id)

    if produto_encontrado:
        # Passa os dados do produto para o HTML
        return render_template("pages/produto.html", produto=produto_encontrado)
    else:
        return "Produto não encontrado", 404


# Carrinho
@app.route("/carrinho")
def carrinho():
    return render_template("pages/carrinho.html")


# Perfil
@app.route("/perfil")
def perfil():
    return render_template("pages/perfil.html")


if __name__ == "__main__":
    app.run(debug=True)
