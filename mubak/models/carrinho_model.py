from database import get_db_connection
from datetime import date


def get_carrinho_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT ic.*, p.nome, p.preco, p.estoque,
                  (SELECT imagem FROM imagem_produto WHERE id_produto=p.id_produto LIMIT 1) AS imagem
           FROM item_carrinho ic
           JOIN produto p ON ic.id_produto = p.id_produto
           WHERE ic.id_usuario=?""",
        (id_usuario,)
    ).fetchall()
    conn.close()
    return rows


def adicionar_ao_carrinho(id_usuario, id_produto, quantidade, preco_unitario):
    conn = get_db_connection()
    existente = conn.execute(
        'SELECT * FROM item_carrinho WHERE id_usuario=? AND id_produto=?',
        (id_usuario, id_produto)
    ).fetchone()

    if existente:
        conn.execute(
            'UPDATE item_carrinho SET quantidade=quantidade+? WHERE id_usuario=? AND id_produto=?',
            (quantidade, id_usuario, id_produto)
        )
    else:
        conn.execute(
            """INSERT INTO item_carrinho (id_usuario, id_produto, quantidade, data_criacao, preco_unitario)
               VALUES (?,?,?,?,?)""",
            (id_usuario, id_produto, quantidade, date.today().isoformat(), preco_unitario)
        )
    conn.commit()
    conn.close()


def atualizar_quantidade(id_usuario, id_produto, quantidade):
    conn = get_db_connection()
    if quantidade <= 0:
        conn.execute(
            'DELETE FROM item_carrinho WHERE id_usuario=? AND id_produto=?',
            (id_usuario, id_produto)
        )
    else:
        conn.execute(
            'UPDATE item_carrinho SET quantidade=? WHERE id_usuario=? AND id_produto=?',
            (quantidade, id_usuario, id_produto)
        )
    conn.commit()
    conn.close()


def remover_do_carrinho(id_usuario, id_produto):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM item_carrinho WHERE id_usuario=? AND id_produto=?',
        (id_usuario, id_produto)
    )
    conn.commit()
    conn.close()


def limpar_carrinho(id_usuario):
    conn = get_db_connection()
    conn.execute('DELETE FROM item_carrinho WHERE id_usuario=?', (id_usuario,))
    conn.commit()
    conn.close()


def total_carrinho(id_usuario):
    itens = get_carrinho_usuario(id_usuario)
    return sum(i['quantidade'] * i['preco_unitario'] for i in itens)
