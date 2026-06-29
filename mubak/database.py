import sqlite3
from config import DATABASE
from werkzeug.security import generate_password_hash


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
            nome varchar(50) NOT NULL,
            descricao varchar(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS produto(
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            nome varchar(50) NOT NULL,
            descricao varchar(100) NOT NULL,
            especificacao_tecncica varchar(100) NOT NULL,
            preco float NOT NULL,
            estoque INT NOT NULL,
            status_prod varchar(50) NOT NULL
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
            imagem longblob NOT NULL,
            id_produto INT NOT NULL,
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

        CREATE TABLE IF NOT EXISTS pedido (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT not null,
            id_endereco INT not null,
            data_pedido DATE not null,
            valor_total DECIMAL(10, 2) not null,
            status_pedido VARCHAR(50) not null,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco)
        );
  
        CREATE TABLE IF NOT EXISTS item_carrinho (
            id_item_carrinho INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT not null,
            id_produto INT not null,
            quantidade INT not null,
            data_criacao DATE not null,
            preco_unitario float not null,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
        );

        CREATE TABLE IF NOT EXISTS item_pedido (
            id_item_pedido INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_pedido INT not null,
            id_produto INT not null,
            quantidade INT not null,
            preco_unitario DECIMAL(10, 2) not null,
            FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
            FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
        );

        CREATE TABLE IF NOT EXISTS pagamento (
            id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_pedido INT not null,
            metodo VARCHAR(50) not null,
            data_pagamento DATE not null,
            valor_pago DECIMAL(10, 2) not null,
            status_pagamento VARCHAR(50) not null,
            detalhes VARCHAR(100) not null,
            FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido)
        );

        CREATE TABLE IF NOT EXISTS notificacao (
            id_notificacao INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            id_usuario INT not null,
            mensagem VARCHAR(255) not null,
            data_notificacao DATE not null,
            status_notificacao VARCHAR(50) not null,
            tipo VARCHAR(50) not null,
            assunto VARCHAR(50) not null,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        );
    """)

    conn.execute(
        """
        INSERT OR IGNORE INTO perfil (id_perfil, tipo)
        VALUES (1, ?)
    """,
        ("Admin",),
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO perfil (id_perfil, tipo)
        VALUES (2, ?)
    """,
        ("Usuario",),
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO usuario (nome, email, senha, telefone, cpf, data_nasc, foto, id_perfil)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """,
        (
            "Admin",
            "admin@gmail.com",
            generate_password_hash("123456"),
            "34038245004",
            "111.111.111-11",
            "1995-05-01",
            "temp.png",
        ),
    )

    conn.commit()
    conn.close()
