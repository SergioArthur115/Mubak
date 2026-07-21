import sqlite3
from config import DATABASE
from werkzeug.security import generate_password_hash
from datetime import date, timedelta


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS perfil(
            id_perfil INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            tipo varchar(20) NOT NULL,
            descricao varchar(100)
        );

        CREATE TABLE IF NOT EXISTS usuario(
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nome varchar(50) NOT NULL,
            email varchar(50) NOT NULL,
            senha varchar(50) NOT NULL,
            telefone varchar(50) NOT NULL,
            cpf varchar(50) UNIQUE NOT NULL,
            data_nasc DATE NOT NULL,
            foto varchar NOT NULL,
            id_perfil INT NOT NULL,
            FOREIGN KEY(id_perfil) REFERENCES perfil(id_perfil)
        );

        CREATE TABLE IF NOT EXISTS categoria(
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nome varchar(50) NOT NULL UNIQUE,
            descricao varchar(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS produto(
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nome varchar(50) NOT NULL,
            descricao varchar(100) NOT NULL,
            especificacao_tecnica varchar(100) NOT NULL,
            preco float NOT NULL,
            estoque INT NOT NULL,
            status_prod varchar(50) NOT NULL,
            id_categoria INT,
            FOREIGN KEY(id_categoria) REFERENCES categoria(id_categoria)
        );

        CREATE TABLE IF NOT EXISTS cupom(
            id_cupom INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            codigo varchar(50) NOT NULL,
            inicio DATE NOT NULL,
            fim DATE NOT NULL,
            valor float NOT NULL,
            ativo boolean NOT NULL
        );

        CREATE TABLE IF NOT EXISTS imagem_produto(
            id_imagem INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            imagem varchar NOT NULL,
            id_produto INT NOT NULL,
            dados BLOB,
            mimetype varchar(50),
            FOREIGN KEY(id_produto) REFERENCES produto(id_produto)
        );

        CREATE TABLE IF NOT EXISTS endereco(
            id_endereco INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            cep varchar(50) NOT NULL,
            bairro varchar(50) NOT NULL,
            cidade varchar(50) NOT NULL,
            estado varchar(50) NOT NULL,
            complemento varchar(50) NOT NULL,
            numero varchar(50) NOT NULL,
            principal boolean NOT NULL,
            id_usuario INT NOT NULL,
            FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario)
        );

        CREATE TABLE IF NOT EXISTS pedido(
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT NOT NULL,
            id_endereco INT NOT NULL,
            data_pedido DATE NOT NULL,
            valor_total DECIMAL(10,2) NOT NULL,
            status_pedido VARCHAR(50) NOT NULL,
            id_cupom INT,
            valor_desconto DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY(id_endereco) REFERENCES endereco(id_endereco),
            FOREIGN KEY(id_cupom) REFERENCES cupom(id_cupom)
        );

        CREATE TABLE IF NOT EXISTS item_carrinho(
            id_item_carrinho INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT NOT NULL,
            id_produto INT NOT NULL,
            quantidade INT NOT NULL,
            data_criacao DATE NOT NULL,
            preco_unitario float NOT NULL,
            FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY(id_produto) REFERENCES produto(id_produto)
        );

        CREATE TABLE IF NOT EXISTS item_pedido(
            id_item_pedido INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_pedido INT NOT NULL,
            id_produto INT NOT NULL,
            quantidade INT NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL,
            FOREIGN KEY(id_pedido) REFERENCES pedido(id_pedido),
            FOREIGN KEY(id_produto) REFERENCES produto(id_produto)
        );

        CREATE TABLE IF NOT EXISTS pagamento(
            id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_pedido INT NOT NULL,
            metodo VARCHAR(50) NOT NULL,
            data_pagamento DATE NOT NULL,
            valor_pago DECIMAL(10,2) NOT NULL,
            status_pagamento VARCHAR(50) NOT NULL,
            detalhes VARCHAR(100) NOT NULL,
            FOREIGN KEY(id_pedido) REFERENCES pedido(id_pedido)
        );

        CREATE TABLE IF NOT EXISTS notificacao(
            id_notificacao INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT NOT NULL,
            mensagem VARCHAR(255) NOT NULL,
            data_notificacao DATE NOT NULL,
            status_notificacao VARCHAR(50) NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            assunto VARCHAR(50) NOT NULL,
            FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario)
        );

        CREATE TABLE IF NOT EXISTS favorito(
            id_favorito INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT NOT NULL,
            id_produto INT NOT NULL,
            data_criacao DATE NOT NULL,
            FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY(id_produto) REFERENCES produto(id_produto),
            UNIQUE(id_usuario, id_produto)
        );
    """)

    # ── Migração: bancos já existentes podem não ter as colunas de cupom em pedido ──
    colunas_pedido = [
        row["name"] for row in conn.execute("PRAGMA table_info(pedido)").fetchall()
    ]
    if "id_cupom" not in colunas_pedido:
        conn.execute("ALTER TABLE pedido ADD COLUMN id_cupom INT")
    if "valor_desconto" not in colunas_pedido:
        conn.execute(
            "ALTER TABLE pedido ADD COLUMN valor_desconto DECIMAL(10,2) DEFAULT 0"
        )

    # ── Migração: bancos já existentes podem não ter as colunas de imagem binária ──
    colunas_imagem = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(imagem_produto)").fetchall()
    ]
    if "dados" not in colunas_imagem:
        conn.execute("ALTER TABLE imagem_produto ADD COLUMN dados BLOB")
    if "mimetype" not in colunas_imagem:
        conn.execute("ALTER TABLE imagem_produto ADD COLUMN mimetype varchar(50)")

    conn.commit()

    # Perfis padrão
    conn.execute("INSERT OR IGNORE INTO perfil (id_perfil, tipo) VALUES (1, 'Admin')")
    conn.execute("INSERT OR IGNORE INTO perfil (id_perfil, tipo) VALUES (2, 'Usuario')")

    # Categorias padrão
    categorias = [
        ("Peças", "Componentes de hardware"),
        ("Computadores", "Desktops e workstations"),
        ("Laptops", "Notebooks e ultrabooks"),
        ("Smartphones", "Celulares e acessórios"),
        ("Monitores", "Telas e displays"),
        ("Acessórios", "Periféricos e acessórios"),
    ]
    for nome, desc in categorias:
        conn.execute(
            "INSERT OR IGNORE INTO categoria (nome, descricao) VALUES (?,?)",
            (nome, desc),
        )

    produtos_exemplo = [
        # Categoria 1: Peças
        (
            1,
            "Placa de Vídeo RTX 5060",
            "Placa de vídeo com Ray Tracing e 8GB GDDR7",
            "8GB GDDR7, 128-bit, DLSS 4.0",
            2299.99,
            10,
            "ativo",
            1,
        ),
        (
            2,
            "SSD NVMe 1TB",
            "Armazenamento de alta velocidade para PC e Laptop",
            "Leitura 3500MB/s, Gravação 3000MB/s, PCIe Gen3",
            420.00,
            25,
            "ativo",
            1,
        ),
        # Categoria 2: Computadores
        (
            3,
            "PC Gamer Aquário Preto",
            "PC Gamer Full Black – Potência, Estilo e Montagem Profissional",
            "Ryzen 7 5700x, 32GB RAM, RTX 5060Ti, SSD 1TB",
            9000.90,
            5,
            "ativo",
            2,
        ),
        # Categoria 3: Laptops
        (
            4,
            "Hp Omen Transcend 14",
            "Laptop leve e potente para trabalho e estudos",
            "Tela 14' OLED, Intel Core Ultra 9, 16GB RAM, SSD 1TB",
            20199.00,
            8,
            "ativo",
            3,
        ),
        # Categoria 4: Smartphones
        (
            5,
            "Celular Xiaomi Poco X8 Pro Max",
            "Celular com bateria de longa duração",
            "Tela 6.83', 512GB, Câmera 50MP, 5G",
            2799.00,
            15,
            "ativo",
            4,
        ),
        # Categoria 5: Monitores
        (
            6,
            "Monitor Gamer Curva Ultrawide Samsung Odyssey G5",
            "Tela Uwqhd com alta taxa de atualização",
            "Painel VA, 1ms de resposta, HDMI/DisplayPort",
            1499.90,
            12,
            "ativo",
            5,
        ),
        # Categoria 6: Acessórios
        (
            7,
            "Teclado Mecânico Gamer Sem Fio Logitech G915 X Lightspeed",
            "Teclado gamer com iluminação",
            "Layout ABNT2, Switches GL Mechanical TACTILE, Anti-ghosting",
            1089.90,
            30,
            "ativo",
            6,
        ),
        (
            8,
            "Mouse Gamer Razer Deathadder Essential",
            "Mouse ergonômico com ajuste de DPI",
            "Até 6400 DPI, 5 botões programáveis, RGB",
            79.90,
            40,
            "ativo",
            6,
        ),
    ]

    for prod in produtos_exemplo:
        conn.execute(
            """
            INSERT OR IGNORE INTO produto (
                id_produto, nome, descricao, especificacao_tecnica, preco, estoque, status_prod, id_categoria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            prod,
        )

    # Admin padrão
    conn.execute(
        """INSERT OR IGNORE INTO usuario
           (nome, email, senha, telefone, cpf, data_nasc, foto, id_perfil)
           VALUES (?,?,?,?,?,?,?,1)""",
        (
            "Admin",
            "admin@gmail.com",
            generate_password_hash("123456"),
            "00000000000",
            "111.111.111-11",
            "1995-05-01",
            "default.png",
        ),
    )

    hoje = date.today()
    validade_longa = (hoje + timedelta(days=365)).isoformat()
    cupons_exemplo = [
        (1, "BEMVINDO10", hoje.isoformat(), validade_longa, 10.0, 1),
        (2, "MUBAK20", hoje.isoformat(), validade_longa, 20.0, 1),
    ]
    for id_cupom, codigo, inicio, fim, valor, ativo in cupons_exemplo:
        conn.execute(
            """INSERT OR IGNORE INTO cupom (id_cupom, codigo, inicio, fim, valor, ativo)
               VALUES (?,?,?,?,?,?)""",
            (id_cupom, codigo, inicio, fim, valor, ativo),
        )

    conn.commit()
    conn.close()
