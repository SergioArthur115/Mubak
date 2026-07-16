from database import get_db_connection
from datetime import date


def criar_pedido(id_usuario, id_endereco, valor_total, id_cupom=None, valor_desconto=0):
    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO pedido
           (id_usuario, id_endereco, data_pedido, valor_total, status_pedido, id_cupom, valor_desconto)
           VALUES (?,?,?,?,?,?,?)""",
        (id_usuario, id_endereco, date.today().isoformat(), valor_total,
         'pendente', id_cupom, valor_desconto)
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


def get_pedido_por_id(id_pedido):
    conn = get_db_connection()
    row = conn.execute(
        """SELECT pe.*, c.codigo AS cupom_codigo
           FROM pedido pe
           LEFT JOIN cupom c ON pe.id_cupom = c.id_cupom
           WHERE pe.id_pedido=?""",
        (id_pedido,)
    ).fetchone()
    conn.close()
    return row


def get_itens_pedido(id_pedido):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT ip.*, p.nome,
                  (SELECT id_imagem FROM imagem_produto
                   WHERE id_produto=p.id_produto ORDER BY id_imagem LIMIT 1) AS id_imagem
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
