from database import get_db_connection
from datetime import date


def criar_pedido(id_usuario, id_endereco, valor_total):
    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO pedido (id_usuario, id_endereco, data_pedido, valor_total, status_pedido)
           VALUES (?,?,?,?,?)""",
        (id_usuario, id_endereco, date.today().isoformat(), valor_total, 'pendente')
    )
    id_pedido = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_pedido


def adicionar_item_pedido(id_pedido, id_produto, quantidade, preco_unitario):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario)
           VALUES (?,?,?,?)""",
        (id_pedido, id_produto, quantidade, preco_unitario)
    )
    conn.commit()
    conn.close()


def get_pedidos_usuario(id_usuario):
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM pedido WHERE id_usuario=? ORDER BY data_pedido DESC',
        (id_usuario,)
    ).fetchall()
    conn.close()
    return rows


def get_itens_pedido(id_pedido):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT ip.*, p.nome,
                  (SELECT imagem FROM imagem_produto WHERE id_produto=p.id_produto LIMIT 1) AS imagem
           FROM item_pedido ip
           JOIN produto p ON ip.id_produto = p.id_produto
           WHERE ip.id_pedido=?""",
        (id_pedido,)
    ).fetchall()
    conn.close()
    return rows


def registrar_pagamento(id_pedido, metodo, valor_pago, detalhes=''):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO pagamento (id_pedido, metodo, data_pagamento, valor_pago, status_pagamento, detalhes)
           VALUES (?,?,?,?,?,?)""",
        (id_pedido, metodo, date.today().isoformat(), valor_pago, 'aprovado', detalhes)
    )
    conn.execute(
        "UPDATE pedido SET status_pedido='pago' WHERE id_pedido=?", (id_pedido,)
    )
    conn.commit()
    conn.close()
