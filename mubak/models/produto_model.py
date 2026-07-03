from database import get_db_connection


# ── Produto ───────────────────────────────────────────────────────────────────

def get_todos_produtos(categoria_nome=None, preco_min=None, preco_max=None, busca=None):
    conn = get_db_connection()

    query = """
        SELECT p.*, c.nome AS categoria_nome,
               (SELECT imagem FROM imagem_produto WHERE id_produto=p.id_produto LIMIT 1) AS imagem
        FROM produto p
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE p.status_prod = 'ativo'
    """
    params = []

    if categoria_nome:
        query += " AND c.nome = ?"
        params.append(categoria_nome)

    if preco_min:
        query += " AND p.preco >= ?"
        params.append(float(preco_min))

    if preco_max:
        query += " AND p.preco <= ?"
        params.append(float(preco_max))

    if busca:
        query += " AND (p.nome LIKE ? OR p.descricao LIKE ?)"
        params.extend([f'%{busca}%', f'%{busca}%'])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_produto_por_id(id_produto):
    conn = get_db_connection()
    produto = conn.execute(
        """SELECT p.*, c.nome AS categoria_nome
           FROM produto p
           LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
           WHERE p.id_produto=?""",
        (id_produto,)
    ).fetchone()
    conn.close()
    return produto


def get_imagens_produto(id_produto):
    conn = get_db_connection()
    imgs = conn.execute(
        'SELECT * FROM imagem_produto WHERE id_produto=?', (id_produto,)
    ).fetchall()
    conn.close()
    return imgs


def criar_produto(nome, descricao, especificacao_tecnica, preco, estoque, id_categoria, status_prod='ativo'):
    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO produto (nome, descricao, especificacao_tecnica, preco, estoque, status_prod, id_categoria)
           VALUES (?,?,?,?,?,?,?)""",
        (nome, descricao, especificacao_tecnica, preco, estoque, status_prod, id_categoria)
    )
    id_novo = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_novo


def atualizar_produto(id_produto, nome, descricao, especificacao_tecnica, preco, estoque, id_categoria, status_prod):
    conn = get_db_connection()
    conn.execute(
        """UPDATE produto
           SET nome=?, descricao=?, especificacao_tecnica=?, preco=?, estoque=?, id_categoria=?, status_prod=?
           WHERE id_produto=?""",
        (nome, descricao, especificacao_tecnica, preco, estoque, id_categoria, status_prod, id_produto)
    )
    conn.commit()
    conn.close()


def deletar_produto(id_produto):
    conn = get_db_connection()
    conn.execute('DELETE FROM imagem_produto WHERE id_produto=?', (id_produto,))
    conn.execute('DELETE FROM favorito WHERE id_produto=?', (id_produto,))
    conn.execute('DELETE FROM produto WHERE id_produto=?', (id_produto,))
    conn.commit()
    conn.close()


def adicionar_imagem_produto(id_produto, nome_arquivo):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO imagem_produto (imagem, id_produto) VALUES (?,?)',
        (nome_arquivo, id_produto)
    )
    conn.commit()
    conn.close()


# ── Categoria ─────────────────────────────────────────────────────────────────

def get_todas_categorias():
    conn = get_db_connection()
    cats = conn.execute('SELECT * FROM categoria').fetchall()
    conn.close()
    return cats


def get_categoria_por_nome(nome):
    conn = get_db_connection()
    cat = conn.execute('SELECT * FROM categoria WHERE nome=?', (nome,)).fetchone()
    conn.close()
    return cat


# ── Promoções (produtos mais baratos como destaque) ───────────────────────────

def get_produtos_destaque(limite=8):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT p.*,
                  (SELECT imagem FROM imagem_produto WHERE id_produto=p.id_produto LIMIT 1) AS imagem
           FROM produto p
           WHERE p.status_prod = 'ativo'
           ORDER BY p.preco ASC
           LIMIT ?""",
        (limite,)
    ).fetchall()
    conn.close()
    return rows
